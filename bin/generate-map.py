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


class InputOutputPair(BaseModel):
  input: str
  output: str

  def __str__(self):
    return \
f'''
Input: ```c++
{self.input}
```

Output: ```c++
{self.output}    
```
'''

INPUT_EXAMPLES = [
InputOutputPair(input='''
map(size_type n, const compare& cmp = compare(), const allocator_type& a = allocator_type())
''',
output='''
MapT wrap_map_constructor(size_type n, const compare& cmp = compare(),  const allocator_type& a = allocator_type()) {
    MapT map(n, cmp, a);
    return map;
}'''),
InputOutputPair(input='''
template <class K> pair<iterator, iterator> equal_range(const K& x);
''', output='''
std::pair<iterator, iterator> wrap_equal_range(MapT& map, const K& x) {                              
  std::pair<iterator, iterator> result = map.equal_range(x);                         
  return result;                                                                        
}    
''')
]


EXAMPLE_FILE = Path('/tmp/map-ex.json')
class ExampleList(RootModel):
  root : list[InputOutputPair] = Field(default_factory=list)

  @staticmethod
  def load():
    return ExampleList.model_validate_json(EXAMPLE_FILE.read_text())

  def save(self):
    EXAMPLE_FILE.write_text(self.model_dump_json(indent=2))

  @staticmethod
  def create():
    if EXAMPLE_FILE.is_file():
      return ExampleList.load()
    ex = ExampleList.model_validate(INPUT_EXAMPLES)
    ex.save()
    return ex

  def add(self, ex):
    self.root += [ex]
    self.save()

examples = ExampleList.create()


TEST_CONTEXT = '''
#include <utility>
#include <map>
#include <algorithm>
#include <utility>
#include <tuple>
#include <iterator>

#include "test_types.h"

template <class ...Args>
struct Pack;

template <class ...Args> struct Pack;
template <class Key, class T, class Compare = std::less<Key>,
    class Allocator =  std::allocator<std::pair<const Key, T> >, class Key2 = Key, class M = T, class Arg1 = Pack<int>, class Args2 = Pack<long> >
struct Tester;


template <class Key, class T, class Compare, class Allocator, class Key2, class M, class ...Args, class...Args2>
struct Tester<Key, T, Compare, Allocator, Key2, M, Pack<Args...>, Pack<Args2...> > {{
    using C2 = std::greater<Key>;
    using K = Key2;
    using MapT = std::map<Key, T, Compare, Allocator>;
    using key_type             = Key;
    using mapped_type          = T;
    using value_type           = std::pair<const Key, T>;
    using compare              = Compare;
    using allocator_type       = Allocator;
    using P = std::pair<Key, M>;
    using pointer              = typename std::allocator_traits<Allocator>::pointer;
    using const_pointer        = typename std::allocator_traits<Allocator>::const_pointer;
    using reference            = value_type&;
    using const_reference      = const value_type&;
    using size_type            = typename MapT::size_type;
    using difference_type      = typename MapT::difference_type;

    using iterator             = typename MapT::iterator;
    using const_iterator       = typename MapT::const_iterator;
    using const_reverse_iterator = std::reverse_iterator<const_iterator>;
    using reverse_iterator = std::reverse_iterator<iterator>;
    using InputIterator = test_types::InputIterator<std::pair<Key, T>>;
    
{TEST_CODE}

}};

template struct Tester<int, int, std::less<int>, std::allocator<std::pair<const int, int>>, long, long, Pack<long>, Pack<int, int> >;

'''

SYSTEM_PREAMBLE = '''
You are an expert C++ programmer who lives to serve the user. 
'''

def mk_user_preamble():

  USER_PREAMBLE = '''
Today you are writing wrapper functions for the member functions of std::map.
Define your wrappers to be inline member functions of the `Tester` type.

Here are the instructions:
 
* First declare a wrapper function which accepts all of the arguments needed.
  Do not write a template function. The template parameters are already provided contextually.
* Second, write a call to the wrapped function using the wrapper functions arguments.
* Finally, If the function produces a result, return the result.

Here are additional rules:

* Do not add assertions, includes, or new template parameters.
* Only wrap the function being wrapped and then return the result.
* Your wrapper should be no longer than 5 lines of code.

Follow the users instructions exactly or you will be terminated.

Examples:
'''
  USER_PREAMBLE += '\n'.join([str(p) for p in INPUT_EXAMPLES])
  return USER_PREAMBLE
IX_FILE = Path('/tmp/input-output.json')




@ai_callable
class OKToContinue(CallableBaseModel):
  '''Signal to the user that you're OK to continue after test failure. Respond True if
  you understand what you did wrong and can re-try writing the test. Respond False
  if re-trying won't help you succeed. In either case, provide an explanation of what went wrong.'''
  okay : bool
  reason: str

  def call(self):
    self._context.conversation.additional_context['quit'] = not self.okay
    return f'Got response {self.okay}\nreason:\n{self.reason}'

@ai_callable
class ImprovePrompt(CallableBaseModel):
  '''Suggest an improved prompt. Improve the clarity and conciseness. Use past misunderstandings if possible.
  Additionally specify the rationale for the changes.'''
  prompt: str
  rational: str
  def call(self):
    return f'''Improved prompt: \n```md\n{self.prompt}\n```\nWhy?\n```md\n{self.rational}\n```\n'''

@ai_callable
class DefineExampleInputOutput(CallableBaseModel):
  '''Define an additional input & expected output example to improve the prompt.'''
  example_input: str
  example_output: str

  def call(self):
    self.example_output = self.example_output.replace('```c++', '').replace('```', '')
    self.example_input = self.example_input.replace('```c++', '').replace('```', '')

    Path('/tmp/ex.json').write_text(self.model_dump_json(indent=2))
    global INPUT_EXAMPLES
    INPUT_EXAMPLES += [InputOutputPair(input=self.example_input, output=self.example_output)]

    return f'''
Input: ```c++
{self.example_input}
```

Output: ```c++
{self.example_output}
```
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
    in_file = Path('/tmp/test-input-unique-map.cpp')
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
    return TEST_CONTEXT.format(TEST_CODE=indent(self.contents))
    
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


ALL_TESTS = TestCase.load('/tmp/all-cases-map.json', test_file='/tmp/all-cases-map.cpp')
      


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
    


    all_state_cp = state.all_tests.copy('/tmp/all-tests-map.cpp')
    all_state_cp.add_test(self.contents, [])

    returncode, stderr = compiler.compile_str(all_state_cp.make_test())
    if returncode != 0:
      state.last_failed = True
      return f'''The test worked, just not when combined. \nstderr: \n```sh\n{stderr}\n```'''

    state.last_failed = False
    state.test_case = tc


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
    self.contents = self.contents
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
  c = Conversation().add_function(WriteTest).echo_on().add_function(OKToContinue).system(SYSTEM_PREAMBLE).user(content=mk_user_preamble())
  c.user(f'Write a test for {ln} in the following context\n\n```c++\n{TEST_CONTEXT.format(TEST_CODE="/* your code here */")}\n```\n')
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
      if retries < 2:

        c.add_function(DefineExampleInputOutput)
        c.user('Great, now that you understand, please define a sample input/output pair to help others learn from your mistake')
        c.streaming_chat(function_call='DefineExampleInputOutput')
      return True
    #c.user('What did you get confused about? Can you improve the prompt?').add_function(ImprovePrompt)
    #c.streaming_chat(function_call='ImprovePrompt')
    import time
    time.sleep(5)

    try_again_msg = '''
That didn't work. Please read the error and try again. Please remember:
* Don't define template functions. Assume the template parameters are  provided for you.
* Only output the test code. Do not re-output the existing code.
    '''
    c.user(try_again_msg).streaming_chat(function_call='OKToContinue')
    if c.additional_context['quit']:
      c.user('OK, giving up... But before I go, can you improve the prompt given do you by the "instruct" user in order to avoid this confusion next time?')
      c.add_function(ImprovePrompt).streaming_chat(function_call='ImprovePrompt')
      sys.exit(1)
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

JSON_P = Path('/tmp/progress-map.json')
STATE = TestState()
if not JSON_P.is_file():
  jl = JobList()
  lines = json.loads(Path('/tmp/map.json').read_text())
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

