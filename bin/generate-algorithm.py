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

ALGORITHM_PREAMBLE = '''
You are an expert C++ programmer who lives to serve the user. 

Today you are writing calls to functions in the STL <algorithm> header.

Here are the rules:

* Output only code. No more than 5 lines.
* The first line should declare a wrapper function which accepts all of the arguments needed. 
* The second line should call the function under tset with those arguments.
* If the function produces a result, return the result on the third line.
* Remove all constexpr keywords.
* Never give an explanation.

Follow the users instructions exactly or you will be terminated.

Examples:

INPUT: 
```c++
template <class ForwardIterator>
constexpr ForwardIterator rotate(ForwardIterator first, ForwardIterator middle, ForwardIterator last);
```

OUTPUT:
```c++
ForwardIterator test_rotate(ForwardIterator first, ForwardIterator middle, ForwardIterator last) {
  return std::rotate(first, middle, last);
}
```

INPUT:
```c++
template <class InputIterator1, class InputIterator2, class OutputIterator>
constexpr OutputIterator
merge(InputIterator1 first1, InputIterator1 last1,
      InputIterator2 first2, InputIterator2 last2, OutputIterator result);
```

OUTPUT:
```c++
OutputIterator test_merge(InputIterator1 first1, InputIterator1 last1,
      InputIterator2 first2, InputIterator2 last2, OutputIterator result) {
  return std::merge(first1, last1, first2, last2, result);     
}
```
'''

TYPE_EXTRACTOR = '''
You are an expert C++ programmer who lives to serve the user. 

Today you are looking at functions in the STL <algorithm> header.
Your job is to extract the template parameter names.

Example:

INPUT: ```c++
template <class InputIterator, class OutputIterator1,
          class OutputIterator2, class Predicate>
    constexpr pair<OutputIterator1, OutputIterator2>   // constexpr in C++20
    partition_copy(InputIterator first, InputIterator last,
                   OutputIterator1 out_true, OutputIterator2 out_false,
                   Predicate pred);
```       

OUTPUT: ```
* InputIterator
* OutputIterator1
* OutputIterator2
* Predicate
```       

Here are the rules:

* Extract every template parameter name.
* Do not modify the names.

Follow the users instructions exactly or you will be terminated.

'''


  
ALGORITHM_FORMAT = '''
#include <algorithm>
#include <iterator>
#include <tuple>
#include <vector>
#include <array>


#include "test_types.h"

using std::iterator_traits;
using std::pair;

template <class T>
struct Tester {{
{DECLARATION_LIST}

{TEST_CODE}
}};

template struct Tester<int>;
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
    return [make_decl(k) for k in self.declaration_keys if k != 'T']
  
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


ALL_TESTS = TestCase.load('/tmp/all-cases.json', test_file='/tmp/all-cases.cpp')
      


@ai_callable
class WriteTest(CallableBaseModel):
  """Save a C++ test to the specified output file.
  The 'output_filename' should be a unique description of the overload + parameters that contains no spaces or special characters.
  The 'contents' should be the test code.
  The 'template_parameter_names' should contain the parameter names as spelled in the template portion of the declaration.
    For example: ```c++
      template <class A, class B> void foo(A a, B b);
    ```
    Output: ```
      * A
      * B
    ```
  """
  output_filename: str
  contents: str 
  template_parameter_names: list[str] = Field(default_factory=list)
  
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
    tc.add_test(contents=self.contents, decl_keys=self.template_parameter_names)
    tc.save()
    case_str = tc.make_test()

    returncode, stderr = compiler.compile(tc.test_file)
    if returncode != 0:
      state.last_failed = True
      tc.test_file.unlink(missing_ok=True)
      return f'''Compilation Failure!\nInput:\n```c++\n{case_str}\n```\nStderr:\n```sh\n{stderr}\n```\n'''
    
    state.last_failed = False
    state.test_case = tc

    all_state_cp = state.all_tests.copy('/tmp/all-tests-copy.cpp')
    all_state_cp.add_test(self.contents, self.template_parameter_names)
    
    returncode, stderr = compiler.compile_str(all_state_cp.make_test())
    if returncode != 0:
      return f'''The test worked, just not when combined. \nstderr: \n```sh\n{stderr}\n```'''
    
    state.all_tests.add_test(self.contents, self.template_parameter_names)
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
  c = Conversation().add_function(WriteTest).system(ALGORITHM_PREAMBLE).echo_on().user(ln)
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
    c.user('Try again please!')
    
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
  lines = json.loads(Path('/tmp/new-list.json').read_text())
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

