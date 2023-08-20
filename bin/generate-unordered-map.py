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

CLASS_DECL = '''```c++
namespace std {
  template<class Key,
           class T,
           class Hash = hash<Key>,
           class Pred = equal_to<Key>,
           class Allocator = allocator<pair<const Key, T>>>
  class unordered_map {
  public:
    // types
    using key_type             = Key;
    using mapped_type          = T;
    using value_type           = pair<const Key, T>;
    using hasher               = Hash;
    using key_equal            = Pred;
    using allocator_type       = Allocator;
    using pointer              = typename allocator_traits<Allocator>::pointer;
    using const_pointer        = typename allocator_traits<Allocator>::const_pointer;
    using reference            = value_type&;
    using const_reference      = const value_type&;
    using size_type            = typename MapT::
    using difference_type      = typename MapT::

    using iterator             = typename MapT::
    using const_iterator       = typename MapT::
    using local_iterator       = typename MapT::
    using const_local_iterator = typename MapT::
    using node_type            = unspecified;
    using insert_return_type   = insert-return-type<iterator, node_type>;

    // [unord.map.cnstr], construct/copy/destroy
    unordered_map();
    explicit unordered_map(size_type n,
                           const hasher& hf = hasher(),
                           const key_equal& eql = key_equal(),
                           const allocator_type& a = allocator_type());
    template<class InputIterator>
      unordered_map(InputIterator f, InputIterator l,
                    size_type n = see below,
                    const hasher& hf = hasher(),
                    const key_equal& eql = key_equal(),
                    const allocator_type& a = allocator_type());

    template<container-compatible-range<value_type> R>
      unordered_map(from_range_t, R&& rg, size_type n = see below,
        const hasher& hf = hasher(), const key_equal& eql = key_equal(),
        const allocator_type& a = allocator_type());
    unordered_map(const unordered_map&);
    unordered_map(unordered_map&&);
    explicit unordered_map(const Allocator&);
    unordered_map(const unordered_map&, const type_identity_t<Allocator>&);
    unordered_map(unordered_map&&, const type_identity_t<Allocator>&);
    unordered_map(initializer_list<value_type> il,
                  size_type n = see below,
                  const hasher& hf = hasher(),
                  const key_equal& eql = key_equal(),
                  const allocator_type& a = allocator_type());
    unordered_map(size_type n, const allocator_type& a)
      : unordered_map(n, hasher(), key_equal(), a) { }
    unordered_map(size_type n, const hasher& hf, const allocator_type& a)
      : unordered_map(n, hf, key_equal(), a) { }
    template<class InputIterator>
      unordered_map(InputIterator f, InputIterator l, size_type n, const allocator_type& a)
        : unordered_map(f, l, n, hasher(), key_equal(), a) { }
    template<class InputIterator>
      unordered_map(InputIterator f, InputIterator l, size_type n, const hasher& hf,
                    const allocator_type& a)
        : unordered_map(f, l, n, hf, key_equal(), a) { }
    template<container-compatible-range<value_type> R>
      unordered_map(from_range_t, R&& rg, size_type n, const allocator_type& a)
        : unordered_map(from_range, std::forward<R>(rg), n, hasher(), key_equal(), a) { }
    template<container-compatible-range<value_type> R>
      unordered_map(from_range_t, R&& rg, size_type n, const hasher& hf, const allocator_type& a)
        : unordered_map(from_range, std::forward<R>(rg), n, hf, key_equal(), a) { }
    unordered_map(initializer_list<value_type> il, size_type n, const allocator_type& a)
      : unordered_map(il, n, hasher(), key_equal(), a) { }
    unordered_map(initializer_list<value_type> il, size_type n, const hasher& hf,
                  const allocator_type& a)
      : unordered_map(il, n, hf, key_equal(), a) { }
    ~unordered_map();
    unordered_map& operator=(const unordered_map&);
    unordered_map& operator=(unordered_map&&)
      noexcept(allocator_traits<Allocator>::is_always_equal::value &&
               is_nothrow_move_assignable_v<Hash> &&
               is_nothrow_move_assignable_v<Pred>);
    unordered_map& operator=(initializer_list<value_type>);
    allocator_type get_allocator() const noexcept;

    // iterators
    iterator       begin() noexcept;
    const_iterator begin() const noexcept;
    iterator       end() noexcept;
    const_iterator end() const noexcept;
    const_iterator cbegin() const noexcept;
    const_iterator cend() const noexcept;

    // capacity
    [[nodiscard]] bool empty() const noexcept;
    size_type size() const noexcept;
    size_type max_size() const noexcept;

    // [unord.map.modifiers], modifiers
    template<class... Args> pair<iterator, bool> emplace(Args&&... args);
    template<class... Args> iterator emplace_hint(const_iterator position, Args&&... args);
    pair<iterator, bool> insert(const value_type& obj);
    pair<iterator, bool> insert(value_type&& obj);
    template<class P> pair<iterator, bool> insert(P&& obj);
    iterator       insert(const_iterator hint, const value_type& obj);
    iterator       insert(const_iterator hint, value_type&& obj);
    template<class P> iterator insert(const_iterator hint, P&& obj);
    template<class InputIterator> void insert(InputIterator first, InputIterator last);
    template<container-compatible-range<value_type> R>
      void insert_range(R&& rg);
    void insert(initializer_list<value_type>);

    node_type extract(const_iterator position);
    node_type extract(const key_type& x);
    template<class K> node_type extract(K&& x);
    insert_return_type insert(node_type&& nh);
    iterator           insert(const_iterator hint, node_type&& nh);

    template<class... Args>
      pair<iterator, bool> try_emplace(const key_type& k, Args&&... args);
    template<class... Args>
      pair<iterator, bool> try_emplace(key_type&& k, Args&&... args);
    template<class K, class... Args>
      pair<iterator, bool> try_emplace(K&& k, Args&&... args);
    template<class... Args>
      iterator try_emplace(const_iterator hint, const key_type& k, Args&&... args);
    template<class... Args>
      iterator try_emplace(const_iterator hint, key_type&& k, Args&&... args);
    template<class K, class... Args>
      iterator try_emplace(const_iterator hint, K&& k, Args&&... args);
    template<class M>
      pair<iterator, bool> insert_or_assign(const key_type& k, M&& obj);
    template<class M>
      pair<iterator, bool> insert_or_assign(key_type&& k, M&& obj);
    template<class K, class M>
      pair<iterator, bool> insert_or_assign(K&& k, M&& obj);
    template<class M>
      iterator insert_or_assign(const_iterator hint, const key_type& k, M&& obj);
    template<class M>
      iterator insert_or_assign(const_iterator hint, key_type&& k, M&& obj);
    template<class K, class M>
      iterator insert_or_assign(const_iterator hint, K&& k, M&& obj);

    iterator  erase(iterator position);
    iterator  erase(const_iterator position);
    size_type erase(const key_type& k);
    template<class K> size_type erase(K&& x);
    iterator  erase(const_iterator first, const_iterator last);
    void      swap(unordered_map&)
      noexcept(allocator_traits<Allocator>::is_always_equal::value &&
               is_nothrow_swappable_v<Hash> &&
               is_nothrow_swappable_v<Pred>);
    void      clear() noexcept;

    template<class H2, class P2>
      void merge(unordered_map<Key, T, H2, P2, Allocator>& source);
    template<class H2, class P2>
      void merge(unordered_map<Key, T, H2, P2, Allocator>&& source);
    template<class H2, class P2>
      void merge(unordered_multimap<Key, T, H2, P2, Allocator>& source);
    template<class H2, class P2>
      void merge(unordered_multimap<Key, T, H2, P2, Allocator>&& source);

    // observers
    hasher hash_function() const;
    key_equal key_eq() const;

    // map operations
    iterator         find(const key_type& k);
    const_iterator   find(const key_type& k) const;
    template<class K>
      iterator       find(const K& k);
    template<class K>
      const_iterator find(const K& k) const;
    size_type        count(const key_type& k) const;
    template<class K>
      size_type      count(const K& k) const;
    bool             contains(const key_type& k) const;
    template<class K>
      bool           contains(const K& k) const;
    pair<iterator, iterator>               equal_range(const key_type& k);
    pair<const_iterator, const_iterator>   equal_range(const key_type& k) const;
    template<class K>
      pair<iterator, iterator>             equal_range(const K& k);
    template<class K>
      pair<const_iterator, const_iterator> equal_range(const K& k) const;

    // [unord.map.elem], element access
    mapped_type& operator[](const key_type& k);
    mapped_type& operator[](key_type&& k);
    template<class K> mapped_type& operator[](K&& k);
    mapped_type& at(const key_type& k);
    const mapped_type& at(const key_type& k) const;
    template<class K> mapped_type& at(const K& k);
    template<class K> const mapped_type& at(const K& k) const;

    // bucket interface
    size_type bucket_count() const noexcept;
    size_type max_bucket_count() const noexcept;
    size_type bucket_size(size_type n) const;
    size_type bucket(const key_type& k) const;
    template<class K> size_type bucket(const K& k) const;
    local_iterator begin(size_type n);
    const_local_iterator begin(size_type n) const;
    local_iterator end(size_type n);
    const_local_iterator end(size_type n) const;
    const_local_iterator cbegin(size_type n) const;
    const_local_iterator cend(size_type n) const;

    // hash policy
    float load_factor() const noexcept;
    float max_load_factor() const noexcept;
    void max_load_factor(float z);
    void rehash(size_type n);
    void reserve(size_type n);
  };
  } // namespace std
```'''

@ai_callable
class DefineList(CallableBaseModel):
  '''Define a list of items as specified by the user'''
  items: list[str]

  def call(self):
    items =  '\n'.join(['\n  * ' + l for l in self.items ])
    self._context.conversation.additional_context['DefineList'] = self.items
    import json
    Path('/tmp/items-unord_map.json').write_text(json.dumps(self.items, indent=2))

    return f'''```md\n{items}\n```\n'''
"""
c = Conversation().echo_on().system('You split C++ class definitions into lists of member functions')
c.user("Please define a list containing each member function present in std::unordered_map").user(CLASS_DECL)
c.add_function(DefineList).streaming_chat(function_call='DefineList')
sys.exit(0)
"""

FUNCTIONAL_PREAMBLE = '''
You are an expert C++ programmer who lives to serve the user. 

Today you are writing calls to member functions of std::unordered_map.

Here are the rules:

* Output only code. No more than 5 lines.
* The first line should declare a wrapper function which accepts all of the arguments needed. .
* The second line should call the function under tset with those arguments.
* If the function produces a result, return the result on the third line.
* Never give an explanation.
* Never add #include's
* Always use the `std::` namespace qualifier.
* The parameters Key, T, Hash, Pred, Allocator, InputIterator, Args..., are already defined.
* Use MapType to mean std::unordered_map<K, V>;

Follow the users instructions exactly or you will be terminated.

Examples:

INPUT: 
```c++
 unordered_map(size_type n, const hasher& hf = hasher(), const key_equal& eql = key_equal(), const allocator_type& a = allocator_type())
```

OUTPUT:
```c++
MapT test_unordered_map_constructor(size_type n, const hasher& hf = hasher(), const key_equal& eql = key_equal(), const allocator_type& a = allocator_type()) {
    MapT map(n, hf, eql, a);
    return map;
}
```


Your code will be placed within the following context.
```c++
#include <utility>
#include <unordered_map>
    
    using MapT = std::unordered_map<Key, T, Hash, Pred, Allocator>;
    using key_type             = Key;
    using mapped_type          = T;
    using value_type           = std::pair<const Key, T>;
    using hasher               = Hash;
    using key_equal            = Pred;
    using allocator_type       = Allocator;
    using pointer              = typename std::allocator_traits<Allocator>::pointer;
    using const_pointer        = typename std::allocator_traits<Allocator>::const_pointer;
    using reference            = value_type&;
    using const_reference      = const value_type&;
    using size_type            = typename MapT::size_type;
    using difference_type      = typename MapT::difference_type;

    using iterator             = typename MapT::iterator;
    using const_iterator       = typename MapT::const_iterator;
    using local_iterator       = typename MapT::local_iterator;
    using const_local_iterator = typename MapT::const_local_iterator;
    using InputIterator = test_types::InputIterator<std::pair<Key, T>>;

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


def do_improve_prompt():
  c = Conversation().echo_on().system("You are a prompt engineer. You're going to help the user rewrite and improve prompts for C++ test writing")
  c.user("Improve the following prompt. It's original purpose was writing C++ tests for std::algorithm. The std::pair. Please rewrite it to prompt the assistant to write tests for std::functional")
  c.user("It's important that the prompt tell the assistant to write the test following the specific rules provided. Do not change the meaning of the rules or rewrite them")
  c.user('Here is the prompt')
  c.user(f'\n```md\n{FUNCTIONAL_PREAMBLE}\n```\n')
  c.add_function(ImprovePrompt).streaming_chat(function_call='ImprovePrompt')

  sys.exit(0)


ALGORITHM_FORMAT = '''
#include <algorithm>
#include <iterator>
#include <tuple>
#include <vector>
#include <array>
#include <utility>
#include <unordered_map>

#include "test_types.h"

template <class ...Args>
struct Pack;

template <class ...Args> struct Pack;
template <class Key, class T, class Hash = std::hash<Key>, class Pred = std::equal_to<Key>, 
    class Allocator =  std::allocator<std::pair<const Key, T> >, class Arg1 = Pack<int> >
struct Tester;



template <class Key, class T, class Hash, class Pred, class Allocator, class ...Args> 
struct Tester<Key, T, Hash, Pred, Allocator, Pack<Args...> > {{
    using MapT = std::unordered_map<Key, T, Hash, Pred, Allocator>;
    using key_type             = Key;
    using mapped_type          = T;
    using value_type           = std::pair<const Key, T>;
    using hasher               = Hash;
    using key_equal            = Pred;
    using allocator_type       = Allocator;
    using pointer              = typename std::allocator_traits<Allocator>::pointer;
    using const_pointer        = typename std::allocator_traits<Allocator>::const_pointer;
    using reference            = value_type&;
    using const_reference      = const value_type&;
    using size_type            = typename MapT::size_type;
    using difference_type      = typename MapT::difference_type;

    using iterator             = typename MapT::iterator;
    using const_iterator       = typename MapT::const_iterator;
    using local_iterator       = typename MapT::local_iterator;
    using const_local_iterator = typename MapT::const_local_iterator;
    using InputIterator = test_types::InputIterator<std::pair<Key, T>>;
  
{DECLARATION_LIST}

{TEST_CODE}
}};

template struct Tester<int, int>;

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


ALL_TESTS = TestCase.load('/tmp/all-cases-umap.json', test_file='/tmp/all-cases-umap.cpp')
      


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

    all_state_cp = state.all_tests.copy('/tmp/all-tests-umap.cpp')
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
    #c.user('What did you get confused about? Can you improve the prompt?').add_function(ImprovePrompt)
    #c.streaming_chat(function_call='ImprovePrompt')
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

JSON_P = Path('/tmp/progress-umap.json')
STATE = TestState()
if not JSON_P.is_file():
  jl = JobList()
  lines = json.loads(Path('/tmp/items-list-umap.json').read_text())
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

