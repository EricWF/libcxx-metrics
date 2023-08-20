import sys
import os

import pydantic_core

sys.path.append(os.path.expanduser('~/shared/python/'))
from elib.ai.conversation import Conversation
from elib.ai.types import *
from elib.ai.functions import *
import subprocess
import shutil
from pydantic import BaseModel, RootModel, Field
from pathlib import Path
import os
import json
from typing import Any, Optional
from pydantic import model_validator

ALLOWED_FAILURES = 5

FUNCTION_DECLS = '''```c++
template<class R, class... ArgTypes>
  class function<R(ArgTypes...)> {
  public:
    using result_type = R;

    // [func.wrap.func.con], construct/copy/destroy
    function() noexcept;
    function(nullptr_t) noexcept;
    function(const function&);
    function(function&&) noexcept;
    template<class F> function(F&&);

    function& operator=(const function&);
    function& operator=(function&&);
    function& operator=(nullptr_t) noexcept;
    template<class F> function& operator=(F&&);
    template<class F> function& operator=(reference_wrapper<F>) noexcept;

    ~function();

    // [func.wrap.func.mod], function modifiers
    void swap(function&) noexcept;

    // [func.wrap.func.cap], function capacity
    explicit operator bool() const noexcept;

    // [func.wrap.func.inv], function invocation
    R operator()(ArgTypes...) const;

    // [func.wrap.func.targ], function target access
    const type_info& target_type() const noexcept;
    template<class T>       T* target() noexcept;
    template<class T> const T* target() const noexcept;
  };

  template<class R, class... ArgTypes>
    function(R(*)(ArgTypes...)) -> function<R(ArgTypes...)>;

  template<class F, class... Args>
  constexpr invoke_result_t<F, Args...> invoke(F&& f, Args&&... args)
    noexcept(is_nothrow_invocable_v<F, Args...>);
    
  template<class F, class... Args>
  constexpr R invoke_r(F&& f, Args&&... args)
    noexcept(is_nothrow_invocable_v<F, Args...>);

};
```'''

@ai_callable
class DefineList(CallableBaseModel):
  '''Define a list of items as specified by the user'''
  items: list[str]

  def call(self):
    items =  '\n'.join(['\n  * ' + l for l in self.items ])
    self._context.conversation.additional_context['DefineList'] = self.items
    import json
    Path('/tmp/items-list.json').write_text(json.dumps(self.items, indent=2))

    return f'''```md\n{items}\n```\n'''


FUNCTIONAL_PREAMBLE = '''
You are an expert C++ programmer who lives to serve the user. 

Today you are writing calls to member functions of std::function.

Here are the rules:

* Output only code. No more than 5 lines.
* The first line should declare a wrapper function which accepts all of the arguments needed. 
* The second line should call the function under tset with those arguments.
* If the function produces a result, return the result on the third line.
* Remove all constexpr keywords.
* Never give an explanation.
* The parameters F, R, Args..., ArgTypes... are already defined.
* Use FunctionType to mean std::function<R(ArgTypes...)>;

Follow the users instructions exactly or you will be terminated.

Examples:

INPUT: 
```c++
function& operator=(nullptr_t) noexcept; 
```

OUTPUT:
```c++
FunctionType& test_function_assign_nullptr(FunctionType& func, std::nullptr_t nsp) {
  return func = nsp;
} 
```

INPUT:
```c++
template<class F> function(F&&);
```

OUTPUT:
```c++
FunctionType test_F_constructor(F&& f) {
  FunctionType func(f);
  return func;
}  
```

Your code will be placed within the following context.
```c++
#include <utility>
#include <functional>


template <class F, class R, class ...Args, class ...ArgTypes>
struct Tester<F, R, Pack<Args...>, Pack<ArgTypes...> > {
  using FuncT = R(ArgTypes...);
  using FunctionType = std::function<R(ArgTypes...)>;
  FunctionType func;
  F f;
  

// YOUR CODE HERE //

};
```

'''






@ai_callable
class ImprovePrompt(CallableBaseModel):
  '''Suggest an improved prompt. Improve the clarity and conciseness. Use past misunderstandings if possible.
  Additionally specify the rationale for the changes.'''
  prompt: str
  rational: str
  def call(self):
    return f'''Improved prompt: \n```md\n{self.prompt}\n```\nWhy?\n```md\n{self.rational}\n```\n'''

"""
c = Conversation().echo_on().system("You are a prompt engineer. You're going to help the user rewrite and improve prompts for C++ test writing")
c.user("Improve the following prompt. It's original purpose was writing C++ tests for std::algorithm. The std::pair. Please rewrite it to prompt the assistant to write tests for std::functional")
c.user("It's important that the prompt tell the assistant to write the test following the specific rules provided. Do not change the meaning of the rules or rewrite them")
c.user('Here is the prompt')
c.user(f'\n```md\n{FUNCTIONAL_PREAMBLE}\n```\n')
c.add_function(ImprovePrompt).streaming_chat(function_call='ImprovePrompt')

sys.exit(0)
"""

ALGORITHM_FORMAT = '''
#include <algorithm>
#include <iterator>
#include <tuple>
#include <vector>
#include <array>
#include <utility>

#include "test_types.h"

template <class ...Args>
struct Pack;

template <class F, class R, class P1, class P2>
struct Tester;

template <class F, class R, class ...Args, class ...ArgTypes>
struct Tester<F, R, Pack<Args...>, Pack<ArgTypes...> > {{
  using FuncT = R(ArgTypes...);
  using FunctionType = std::function<R(ArgTypes...)>;
  
{DECLARATION_LIST}

{TEST_CODE}
}};

template struct Tester<int(*)(int, const char*), int, Pack<float, char*>, Pack<int, const char*> >;
'''


def find_last_match(lst, condition):
    return next((x for x in reversed(lst) if condition(x)), None)


def find_first_match(lst, condition):
    return next((x for x in lst if condition(x)), None)


class Compiler(BaseModel):
  compiler: Path = Field(default_factory=lambda: Path(shutil.which('clang++')))
  flags: list[str] = Field(default_factory=list)
  linker_flags: list[str] = Field(default_factory=list)
  
  @staticmethod
  def include_root():
    INCLUDE_ROOT = Path(os.path.expanduser('~/other-workspace/libcxx-metrics/inputs/include'))
    assert INCLUDE_ROOT.is_dir()
    return str(INCLUDE_ROOT)

  
  def compile(self, input_file, output_file='/dev/null', flags=[]):
    inv = [str(self.compiler)]  + self.flags + flags + ['-xc++', '-c', '-ferror-limit=1',
          '-I', str(Compiler.include_root()), '-o', str(output_file), str(input_file)]
    proc = subprocess.Popen(inv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out,_ = proc.communicate()
    out = out.decode('utf-8')
    import humanfriendly.terminal as term
    out = term.ansi_strip(out)
    assert proc.poll() is not None
    assert proc.returncode is not None
    return proc.returncode, out
  
  def compile_str(self, test_code, flags=[]):
    in_file = Path('/tmp/test-input-unique.cpp')
    p = test_code
    in_file.write_text(p)
    return self.compile(in_file, flags=flags)
  

def  make_decl(key):
    if key == 'T':
      raise RuntimeError('T is already provided')

    if key == 'Generator':
      return 'using Generator = test_types::Sink<T>;'
    if key == 'PopulationIterator' or key == 'SampleIterator':
      return f'using {key} = test_types::ForwardIterator<T>;'
    if 'Iterator' in key:
      if key[-1].isdigit():
        return f'using {key} = test_types::{key[:-1]}<T>;'
      else:
        return f'using {key} = test_types::{key}<T>;'
    else:
      return f'using {key} = test_types::{key};'

class TestCase(BaseModel):
  declaration_keys: list[str] = Field(default_factory=list)
  contents: str
  test_file: Path
  json_path: Optional[Path] = Field(exclude=True, default=None)

  def copy(self, test_file):
    cp = self.model_copy(deep=True)
    cp.json_path = None
    cp.test_file = Path(test_file)
    return cp

  def get_declarations(self):
    return [] #[make_decl(k) for k in self.declaration_keys if k != 'T']
  
  def make_test(self):
    def indent(input):
      lines = input.splitlines()
      return '\n'.join(['    ' + i for i in lines])
    return ALGORITHM_FORMAT.format(DECLARATION_LIST=indent('\n'.join(self.get_declarations())), TEST_CODE=indent(self.contents))
    
  def add_test(self, contents, decl_keys):
    self.contents += '\n\n' + contents
    for k in decl_keys:
      if k not in self.declaration_keys:
        self.declaration_keys += [k]
    
  def save(self):
    self.test_file.write_text(self.make_test())
    if self.json_path:
      self.json_path.write_text(self.model_dump_json(indent=2))

  @staticmethod
  def load(p, *, test_file, create=True):
    p = Path(p)
    if not p.is_file():
      c = TestCase.model_validate({'json_path': p, 'test_file': Path(test_file), 'contents': ''})
      c.save()
    res = TestCase.model_validate_json(Path(p).read_text())
    res.json_path = p
    return res


ALL_TESTS = TestCase.load('/tmp/all-cases-pair.json', test_file='/tmp/all-cases-pair.cpp')
      


@ai_callable
class WriteTest(CallableBaseModel):
  """Save a C++ test to the specified output file.
  The 'output_filename' should be a unique description of the overload + parameters that contains no spaces or special characters.
  The 'contents' should be the test code.
  """
  output_filename: str
  contents: str


  def get_input(self):
    msgs = self._context.conversation.messages
    m = find_first_match(msgs, lambda m: m.role == 'user')
    return m.content
    
  
  def call(self):
    state = self._context.conversation.additional_context['STATE']
    state.last_failed = True
    state.test_case = None
    compiler = Compiler(flags=['-std=c++17', '-fsyntax-only'])
    global ALL_TESTS
    
    tc = TestCase(contents='', test_file=self.build_filename())
    tc.add_test(contents=self.contents, decl_keys=[])
    tc.save()
    case_str = tc.make_test()

    returncode, stderr = compiler.compile(tc.test_file)
    if returncode != 0:
      state.last_failed = True
      tc.test_file.unlink(missing_ok=True)
      return f'''Compilation Failure!\nInput:\n```c++\n{case_str}\n```\nStderr:\n```sh\n{stderr}\n```\n'''
    
    state.last_failed = False
    state.test_case = tc

    all_state_cp = state.all_tests.copy('/tmp/all-tests-func.cpp')
    all_state_cp.add_test(self.contents, [])
    
    returncode, stderr = compiler.compile_str(all_state_cp.make_test())
    if returncode != 0:
      return f'''The test worked, just not when combined. \nstderr: \n```sh\n{stderr}\n```'''
    
    state.all_tests.add_test(self.contents, [])
    state.save()
    return f'''Well code! That was amazing. Test written to {tc.test_file}'''
      
      
  def build_filename(self):
    filename = Path(self.output_filename)
    base = filename.parent
    ext = filename.suffix
    if not ext:
      ext = '.cpp'
    stem = filename.stem
    self.contents = f'/* {self.get_input()}  */\n' + self.contents
    contents = self.contents.replace('TESTNAME', stem)
    ROOT = Path('/tmp/root')
    def build_name():
      test_root = ROOT / base
      assert test_root.is_dir()
      test_p = test_root / f'{stem}{ext}'
      if not test_p.exists():
        return test_p
      for i in range(0, 5):
        new_n = test_root / f'{stem}-{i}{ext}'
        if not new_n.exists():
          return new_n
      raise RuntimeError("Failed to create unique filename")
    return build_name()

class TestState(BaseModel):
  last_failed : bool = Field(default=True)
  test_case: Optional[TestCase] = Field(default=None)
  all_tests: TestCase = Field(default_factory=lambda: ALL_TESTS)
  
  def save(self):
    self.all_tests.save()
  
def do_it(ln, state):
  retries = 3
  c = Conversation().add_function(WriteTest).system(FUNCTIONAL_PREAMBLE).echo_on().user(ln)
  c.additional_context['STATE'] = state
  while retries >= 0:
    retries -= 1
    try:
      c.streaming_chat(function_call='WriteTest')
    except pydantic_core.ValidationError as VD:
      import rich
      rich.print(VD)
    except Exception as E:
     raise E
    if not state.last_failed:
      return True
    c.user('What did you get confused about? Can you improve the prompt?').add_function(ImprovePrompt)
    c.streaming_chat(function_call='ImprovePrompt')
    import time
    time.sleep(5)
    c.user('OK, now please try again!')
    
  return False




class Job(BaseModel):
  input: str
  output_file: Optional[str] = Field(default=None)
  done: bool = Field(default=False)
  
class JobList(RootModel):
  root: list[Job] = Field(default_factory=list)
  
  def save(self, p):
    p.write_text(self.model_dump_json(indent=2))
    
  @staticmethod
  def load(p):
    return  JobList.model_validate_json(p.read_text())

JSON_P = Path('/tmp/progress.json')
STATE = TestState()
if not JSON_P.is_file():
  jl = JobList()
  lines = json.loads(Path('/tmp/items-list.json').read_text())
  for l in lines:
    jl.root.append(Job(input=l, done=False))
  jl.save(JSON_P)
  
JOBS = JobList.load(JSON_P)
import tqdm
for j in tqdm.tqdm(JOBS.root):
  if j.done:
    continue
  res = do_it(j.input, STATE)
  if res:
    j.done = True
    j.output_file = None
    JOBS.save(JSON_P)

