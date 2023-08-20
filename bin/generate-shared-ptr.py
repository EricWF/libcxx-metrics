from elib.ai.conversation import Conversation
from elib.ai.types import *
from elib.ai.functions import *
import subprocess
import shutil
from pydantic import BaseModel, RootModel, Field

PROMPT_SHARED_PTR = '''
You are an expert C++ programmer who lives to serve the user. 

Today you are writing calls to std::shared_ptr<T>'s member functions and constructors.

Here are the rules:

* Output only code. No more than 5 lines.
* The first line should declare a wrapper function which accepts all of the arguments needed. 
* The second line should call the function under tset with those arguments.
* If the function produces a result or is a constructor, return the result on the third line.
* Never give an explanation.
* The user will handle the preamble, Write only the call to the specified function.

Follow the users instructions exactly or you will be terminated.

Examples:

INPUT: 

template<class Y> explicit shared_ptr(Y* p);

OUTPUT:

auto TESTNAME(Y* y) {
  std::shared_ptr<T> result(yp);
  return result
}

INPUT:

template <class D, class A> shared_ptr(nullptr_t p, D d, A a);

OUTPUT:

auto TESTNAME(nullptr_t p, D d, A a) {
  std::shared_ptr<T> result(p, d, a);
  return result;
}

INPUT:

template<class Y> void reset(Y* p);

OUTPUT:

auto TESTNAME(std::shared_ptr<T> self, Y* p) {
    return self.reset(p);
}

'''

ALGORITHM_PREAMBLE =
'''
You are an expert C++ programmer who lives to serve the user. 

Today you are writing calls to std::shared_ptr<T>'s member functions and constructors.

Here are the rules:

* Output only code. No more than 5 lines.
* The first line should declare a wrapper function which accepts all of the arguments needed. 
* The second line should call the function under tset with those arguments.
* If the function produces a result or is a constructor, return the result on the third line.
* Never give an explanation.
* The user will handle the preamble, Write only the call to the specified function.

Follow the users instructions exactly or you will be terminated.

Examples:

INPUT: 

template<class Y> explicit shared_ptr(Y* p);

OUTPUT:

auto TESTNAME(Y* y) {
  std::shared_ptr<T> result(yp);
  return result
}

INPUT:

template <class D, class A> shared_ptr(nullptr_t p, D d, A a);

OUTPUT:

auto TESTNAME(nullptr_t p, D d, A a) {
  std::shared_ptr<T> result(p, d, a);
  return result;
}

INPUT:

template<class Y> void reset(Y* p);

OUTPUT:

auto TESTNAME(std::shared_ptr<T> self, Y* p) {
    return self.reset(p);
}
'''

SHARED_PTR_PREAMBLE =  '''
#include <memory>
#include <utility>
#include <type_traits>
struct Base { explicit Base(int); Base() = default; Base(Base const&) = default; Base(Base&&) = default; };
struct Derived : Base {};
using T = Base;
using Y = Derived;
using A = std::allocator<Base>;
using D = std::default_delete<Base>;
#define CONCAT2(x, y) x ## y
#define CONCAT(x, y) CONCAT2(x, y)
#define TESTNAME CONCAT(test_case, __COUNTER__)

'''

ALGORITHM_PREAMBLE = '''
#include <algorithm>
#include <iterator>
#include <tuple>
#include <vector>
#include <array>

#include "test_types.h"
template <class Ret>
struct Universal {
  template <class ...Args>
  Ret operator()(Args&&...args) const;
};
using Predicate = Universal<bool>;
using BinaryPredicate = Predicate;
using Compare = Predicate;

using T = int;
using InputIterator = T*;
using InputIterator1 = InputIterator;
using OutputIterator = T*;
using BidirectionalIterator = T*;
using RandomAccessIterator = T*;
extern RandomAccessIterator first, last, first1, last1, first2, last2, middle, result;
extern T value;
extern Compare compare, comp;
extern Predicate predicate, pre;
'''



def find_last_match(lst, condition):
    return next((x for x in reversed(lst) if condition(x)), None)


def find_first_match(lst, condition):
    return next((x for x in lst if condition(x)), None)


LAST_FAILED = False
LAST_OUTPUT = None
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
    global LAST_FAILED
    global LAST_OUTPUT
    LAST_FAILED = True
    LAST_OUTPUT = None
    filename = Path(self.output_filename)
    base = filename.parent
    ext = filename.suffix
    if not ext:
      ext = '.cpp'
    stem = filename.stem
    self.contents = f'// {self.get_input()}\n' + self.contents
    contents = self.contents.replace('TESTNAME', stem)
    ROOT = Path('/tmp/root')
    def build_name():
      test_root = ROOT / base
      assert test_root.is_dir()
      test_p = test_root / f'{stem}{ext}'
      if not test_p.exists():
        return test_p
      for i in range(0, 5):
        new_n = test_root / f'{stem}-{idx}{ext}'
        if not new_n.exists():
          return new_n
      raise RuntimeError("Failed to create unique filename")
    
    ROOT = Path('/tmp/root')
    
    
    preamble =
    good = Path('/tmp/root/good.cc')
    good_cp = Path('/tmp/good_cp.cc')
    if not good.exists():
      good.write_text(preamble)
    shutil.copy(good, good_cp)
    Path('/tmp/test.cc').write_text(preamble + contents)
    
    returncode, stderr = self.compile('/tmp/test.cc')
    if returncode != 0:
      return f'''That test failed with error: \n\n```bash\n{stderr}\n```\n\nTry again!'''
    
    out = build_name()
    out.write_text(contents)
    
    cp_txt = good_cp.read_text()
    cp_txt += '\n' + contents
    good_cp.write_text(cp_txt)
    returncode, stderr = self.compile(good_cp)
    LAST_FAILED = False
    LAST_OUTPUT = out
    if returncode != 0:
      return f'''That failed weirdly, but we'll accept it...\n\nstderr:\n{stderr}\n'''
    good.write_text(cp_txt)
    
    return f'Good job, nice test! Written to {out}'
    
  def compile(self, fname):
    
    proc = subprocess.Popen(['clang++', '-std=c++14', '-xc++', '-fsyntax-only',
       '-o', '/dev/null', str(fname)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out,err = proc.communicate()
    out = out.decode('utf-8').strip()
    import humanfriendly.terminal
    return proc.returncode, humanfriendly.terminal.ansi_strip(out)
  
    

def do_it(ln):
  retries = 3
  c = Conversation().add_function(WriteTest).system(PROMPT).echo_on().user(ln)
  while retries >= 0:
    retries -= 1
    try: 
      c.streaming_chat(function_call='WriteTest')
    except Exception as E:
      import rich
      print = rich.print
      print('Failed with exception: %s' % E)
      print(E.__traceback__)
    if not LAST_FAILED:
      return True, LAST_OUTPUT
    c.user('Try again please!')
    
  return False, None

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
if not JSON_P.is_file():
  jl = JobList()
  lines = [l.strip() for l in Path('/tmp/desc.cpp').read_text().splitlines() if l.strip()]
  for l in lines:
    jl.root.append(Job(input=l, done=False))
  jl.save(JSON_P)
  
JOBS = JobList.load(JSON_P)
import tqdm
for j in tqdm.tqdm(JOBS.root):
  if j.done:
    continue
  res, output = do_it(j.input)
  if res:
    j.done = True
    j.output_file = str(output)
    JOBS.save(JSON_P)
