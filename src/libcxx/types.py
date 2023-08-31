import contextlib
import os, sys, rich, json, re, shutil
from pathlib import Path
from pydantic import BaseModel, Field, RootModel
from typing import Union, Optional, Any, Annotated, Literal
from libcxx.config import LIBCXX_VERSIONS_ROOT, LIBCXX_INPUTS_ROOT, LLVM_PROJECT_ROOT
import copy
from enum import Enum
import subprocess

CLANG_VERSIONED_RE = re.compile('clang-(?P<MAJOR>\d{1,2})(?P<MINOR>\.\d)(?P<PATCHLEVEL>\.\d)?')
CLANG_TRUNK_RE = re.compile('clang-trunk-(?P<YEAR>\d\d\d\d)(?P<MONTH>\d\d)(?P<DAY>\d\d)')

assert CLANG_VERSIONED_RE.match('clang-15.0.0')
assert CLANG_TRUNK_RE.match('clang-trunk-20230301')

class Datestamp(BaseModel):
  kind : Literal['datestamp'] = 'datestamp'
  year : int
  month : int
  day : int

  @staticmethod
  def from_match(m):
    assert m is not None
    keys = ['YEAR', 'MONTH', 'DAY']
    return Datestamp.model_validate({k.lower(): int(m[k]) for k in keys})

  def to_string(self):
    return f'trunk-{self.year:04d}{self.month:02d}{self.day:02d}'

  def __eq__(self, other):
    if not isinstance(other, Datestamp):
      return False
    return self.key() == other.key()

  def __lt__(self, other):
    if isinstance(other, Version):
      return False
    if not isinstance(other, Datestamp):
      raise RuntimeError('Cannot compare to type %s' % type(other))
    return self.key() < other.key()

  def key(self):
    return (self.year, self.month, self.day, )

class Version(BaseModel):
  kind: Literal['version'] = 'version'
  major : int = 0
  minor : int = 0
  patchlevel : int = 0

  @staticmethod
  def from_match(m):
    assert m is not None
    keys = ['MAJOR', 'MINOR', 'PATCHLEVEL']
    return Version.model_validate({k.lower(): int(str(m[k] if m[k] is not None else '0').replace('.', '')) for k in keys})

  def to_string(self):
    return f'{self.major}.{self.minor}.{self.patchlevel}'

  def __eq__(self, other):
    if not isinstance(other, Version):
      return False
    return self.key() == other.key()

  def __lt__(self, other):
    if isinstance(other, Datestamp):
      return True
    if not isinstance(other, Version):
      raise RuntimeError('Cannot compare to type %s' % type(other))
    return self.key() < other.key()

  def key(self):
    return (self.major, self.minor, self.patchlevel, )

  def __hash__(self):
    return hash(self.key())

LIBRARY_NAMES = ['libc++', 'libc++abi', 'libc++experimental']

Identifier = Annotated[Union[Version, Datestamp], Field(discriminator='kind')]

class Standard(str, Enum):
  Cpp03 ='c++03',
  Cpp11 = 'c++11'
  Cpp14 = 'c++14'
  Cpp17 = 'c++17'
  Cpp20 = 'c++20'
  Cpp23 = 'c++23'
  Cpp26 = 'c++26'


  @staticmethod
  def convert(ins):
    return Standard.alt_mappings()[ins]

  @staticmethod
  def alt_mappings():
    m = {}
    for s in Standard:
      v = int(s.replace('c++', ''))
      m[v] = s
      m[s.value] = s
      m[v + 2000] = s
      m[f'{v:02d}'] = s
      m[f'{v + 2000}'] = s
      m[s.replace('c++', 'Cpp')] = s
    return m

  @staticmethod
  def between(v1, v2):
    vlist = [v for v in Standard]
    result = []
    idx1 = vlist.index(v1)
    idx2 = vlist.index(v2)
    assert idx1 < idx2
    return vlist[idx1:idx2 + 1]

  @staticmethod
  def after(v1):
    vlist = [v for v in Standard]
    return vlist[vlist.index(v1):]

  @staticmethod
  def before(v1):
    vlist = [v for v in Standard]
    return vlist[:vlist.index(v1)]


  def aliases(self):
    amap = {
        Standard.Cpp20: ['c++2a'],
        Standard.Cpp23: ['c++2b']
    }
    if self in amap:
      return amap[self]
    return []



  def flag(self):
    aliases = self.aliases()
    if aliases:
      return f'-std={aliases[0]}'
    return f'-std={self.value}'

  def to_year(self):
    num = int(self.value.replace('c++', ''))
    return 2000 + num

  def __lt__(self, other):
    if not isinstance(other, Standard):
      raise RuntimeError("Unexpected type. expected Standard got %s" % type(other))
    return self.to_year() < other.to_year()


class LibcxxVersion(str, Enum):
  installed = "installed",
  installed_libstdcxx = "installed_libstdcxx",
  v4 = '4.0.1',
  v5 = '5.0.1'
  v6 = '6.0.1'
  v7 = '7.1.0'
  v8 = '8.0.1'
  v9 = '9.0.1'
  v10 = '10.0.1'
  v11 = '11.0.1'
  v12 = '12.0.1'
  v13 = '13.0.1'
  v14 = '14.0.0'
  v15 = '15.0.0'
  v16 = '16.0.0'
  trunk = 'trunk'


  @staticmethod
  def between(v1, v2):
    vlist = [v for v in LibcxxVersion]
    result = []
    idx1 = vlist.index(v1)
    idx2 = vlist.index(v2)
    assert idx1 < idx2
    return vlist[idx1:idx2 + 1]

  @staticmethod
  def after(v1):
    vlist = [v for v in LibcxxVersion]
    return vlist[vlist.index(v1):]

  @staticmethod
  def before(v1):
    vlist = [v for v in LibcxxVersion]
    return vlist[:vlist.index(v1)]

  def git_tag(self):
    if self == LibcxxVersion.trunk:
      return 'main'
    else:
      return f'llvmorg-{self.value}'



  def load(self, root=LIBCXX_VERSIONS_ROOT):
    root = Path(root).absolute()
    key = None
    if self.value == 'trunk':
      bits = list(root.glob('trunk-*'))
      def sort_trunk(x):
        x = x.name
        parts = x.split('-')
        assert len(parts) == 2
        return int(parts[1])
      bits.sort(key=sort_trunk)
      key = bits[-1]
    else:
      key = self.value
    p = Path(root / key / 'info.json')
    if not p.is_file():
      raise RuntimeError('Failed to find file: %s' % p)
    return LibcxxInfo.create_from_path(p)

  def _to_tuple(self):
    if self.value == 'trunk':
      return (2023, 99, 99,)
    parts = self.value.split('.')
    return tuple([int(p) for p in parts])

  def __lt__(self, other):
    if not isinstance(other, LibcxxVersion):
      raise RuntimeError("expected LibcxxVersion type, got %s" % type(other))
    return self._to_tuple() < other._to_tuple()



class STLHeader(str, Enum):
  algorithm = "algorithm"
  any = "any"
  array = "array"
  atomic = "atomic"
  barrier = "barrier"
  bit = "bit"
  bitset = "bitset"
  cassert = "cassert"
  ccomplex = "ccomplex"
  cctype = "cctype"
  cerrno = "cerrno"
  cfenv = "cfenv"
  cfloat = "cfloat"
  charconv = "charconv"
  chrono = "chrono"
  cinttypes = "cinttypes"
  ciso646 = "ciso646"
  climits = "climits"
  clocale = "clocale"
  cmath = "cmath"
  codecvt = "codecvt"
  compare = "compare"
  complex = "complex"
  complex_h = "complex.h"
  concepts = "concepts"
  condition_variable = "condition_variable"
  coroutine = "coroutine"
  csetjmp = "csetjmp"
  csignal = "csignal"
  cstdarg = "cstdarg"
  cstdbool = "cstdbool"
  cstddef = "cstddef"
  cstdint = "cstdint"
  cstdio = "cstdio"
  cstdlib = "cstdlib"
  cstring = "cstring"
  ctgmath = "ctgmath"
  ctime = "ctime"
  ctype_h = "ctype.h"
  cuchar = "cuchar"
  cwchar = "cwchar"
  cwctype = "cwctype"
  deque = "deque"
  errno_h = "errno.h"
  exception = "exception"
  execution = "execution"
  expected = "expected"
  fenv_h = "fenv.h"
  filesystem = "filesystem"
  float_h = "float.h"
  format = "format"
  forward_list = "forward_list"
  fstream = "fstream"
  functional = "functional"
  future = "future"
  initializer_list = "initializer_list"
  inttypes_h = "inttypes.h"
  iomanip = "iomanip"
  ios = "ios"
  iosfwd = "iosfwd"
  iostream = "iostream"
  istream = "istream"
  iterator = "iterator"
  latch = "latch"
  limits = "limits"
  limits_h = "limits.h"
  list = "list"
  locale = "locale"
  locale_h = "locale.h"
  map = "map"
  math_h = "math.h"
  mdspan = "mdspan"
  memory = "memory"
  memory_resource = "memory_resource"
  mutex = "mutex"
  new = "new"
  numbers = "numbers"
  numeric = "numeric"
  optional = "optional"
  ostream = "ostream"
  print = "print"
  queue = "queue"
  random = "random"
  ranges = "ranges"
  ratio = "ratio"
  regex = "regex"
  scoped_allocator = "scoped_allocator"
  semaphore = "semaphore"
  set = "set"
  setjmp_h = "setjmp.h"
  shared_mutex = "shared_mutex"
  source_location = "source_location"
  span = "span"
  sstream = "sstream"
  stack = "stack"
  stdatomic_h = "stdatomic.h"
  stdbool_h = "stdbool.h"
  stddef_h = "stddef.h"
  stdexcept = "stdexcept"
  stdint_h = "stdint.h"
  stdio_h = "stdio.h"
  stdlib_h = "stdlib.h"
  stop_token = "stop_token"
  streambuf = "streambuf"
  string = "string"
  string_h = "string.h"
  string_view = "string_view"
  strstream = "strstream"
  system_error = "system_error"
  tgmath_h = "tgmath.h"
  thread = "thread"
  tuple = "tuple"
  typeindex = "typeindex"
  typeinfo = "typeinfo"
  type_traits = "type_traits"
  uchar_h = "uchar.h"
  unordered_map = "unordered_map"
  unordered_set = "unordered_set"
  utility = "utility"
  valarray = "valarray"
  variant = "variant"
  vector = "vector"
  version = "version"
  wchar_h = "wchar.h"
  wctype_h = "wctype.h"

  def __lt__(self, other):
    if not isinstance(other, STLHeader):
      raise RuntimeError('Cannot compare types STLHeader and %s' % type(other))
    return self.value < other.value

  @staticmethod
  def value_map():
    res = {}
    for k in STLHeader:
      res[k.value] = k
    return res

  def resolve(self, s):
    for k in STLHeader:
      if k.value == s:
        return k
    raise ValueError("Could not find header %s")

  def is_c_header(self):
    return self.value.endswith('.h')

  def dialect(self) -> Standard:
    """Return the first dialect containing the standard"""
    dmap = {
        STLHeader.algorithm           : Standard.Cpp03,
        STLHeader.any                 : Standard.Cpp17,
        STLHeader.array               : Standard.Cpp11,
        STLHeader.atomic              : Standard.Cpp11,
        STLHeader.barrier             : Standard.Cpp20,
        STLHeader.bit                 : Standard.Cpp20,
        STLHeader.bitset              : Standard.Cpp03,
        STLHeader.cassert             : Standard.Cpp03,
        STLHeader.ccomplex            : Standard.Cpp11,
        STLHeader.cctype              : Standard.Cpp03,
        STLHeader.cerrno              : Standard.Cpp03,
        STLHeader.cfenv               : Standard.Cpp11,
        STLHeader.cfloat              : Standard.Cpp11,
        STLHeader.charconv            : Standard.Cpp17,
        STLHeader.chrono              : Standard.Cpp11,
        STLHeader.cinttypes           : Standard.Cpp11,
        STLHeader.ciso646             : Standard.Cpp03,
        STLHeader.climits             : Standard.Cpp03,
        STLHeader.clocale             : Standard.Cpp03,
        STLHeader.cmath               : Standard.Cpp03,
        STLHeader.codecvt             : Standard.Cpp11,
        STLHeader.compare             : Standard.Cpp20,
        STLHeader.complex             : Standard.Cpp03,
        STLHeader.complex_h           : Standard.Cpp03,
        STLHeader.concepts            : Standard.Cpp20,
        STLHeader.condition_variable  : Standard.Cpp11,
        STLHeader.coroutine           : Standard.Cpp20,
        STLHeader.csetjmp             : Standard.Cpp11,
        STLHeader.csignal             : Standard.Cpp03,
        STLHeader.cstdarg             : Standard.Cpp03,
        STLHeader.cstdbool            : Standard.Cpp11,
        STLHeader.cstddef             : Standard.Cpp03,
        STLHeader.cstdint             : Standard.Cpp11,
        STLHeader.cstdio              : Standard.Cpp03,
        STLHeader.cstdlib             : Standard.Cpp03,
        STLHeader.cstring             : Standard.Cpp03,
        STLHeader.ctgmath             : Standard.Cpp11,
        STLHeader.ctime               : Standard.Cpp03,
        STLHeader.ctype_h             : Standard.Cpp03,
        STLHeader.cuchar              : Standard.Cpp11,
        STLHeader.cwchar              : Standard.Cpp03,
        STLHeader.cwctype             : Standard.Cpp11,
        STLHeader.deque               : Standard.Cpp03,
        STLHeader.errno_h             : Standard.Cpp03,
        STLHeader.exception           : Standard.Cpp03,
        STLHeader.execution           : Standard.Cpp17,
        STLHeader.expected            : Standard.Cpp23, # IDX
        STLHeader.fenv_h              : Standard.Cpp11,
        STLHeader.filesystem          : Standard.Cpp17,
        STLHeader.float_h             : Standard.Cpp03,
        STLHeader.format              : Standard.Cpp20,
        STLHeader.forward_list        : Standard.Cpp11,
        STLHeader.fstream             : Standard.Cpp03,
        STLHeader.functional          : Standard.Cpp11,
        STLHeader.future              : Standard.Cpp11,
        STLHeader.initializer_list    : Standard.Cpp11,
        STLHeader.inttypes_h          : Standard.Cpp11,
        STLHeader.iomanip             : Standard.Cpp03,
        STLHeader.ios                 : Standard.Cpp03,
        STLHeader.iosfwd              : Standard.Cpp03,
        STLHeader.iostream            : Standard.Cpp03,
        STLHeader.istream             : Standard.Cpp03,
        STLHeader.iterator            : Standard.Cpp03,
        STLHeader.latch               : Standard.Cpp20,
        STLHeader.limits              : Standard.Cpp03,
        STLHeader.limits_h            : Standard.Cpp03,
        STLHeader.list                : Standard.Cpp03,
        STLHeader.locale              : Standard.Cpp03,
        STLHeader.locale_h            : Standard.Cpp03,
        STLHeader.map                 : Standard.Cpp03,
        STLHeader.math_h              : Standard.Cpp03,
        STLHeader.mdspan              : Standard.Cpp23,
        STLHeader.memory              : Standard.Cpp11,
        STLHeader.memory_resource     : Standard.Cpp17,
        STLHeader.mutex               : Standard.Cpp11,
        STLHeader.new                 : Standard.Cpp03,
        STLHeader.numbers             : Standard.Cpp20,
        STLHeader.numeric             : Standard.Cpp03,
        STLHeader.optional            : Standard.Cpp17,
        STLHeader.ostream             : Standard.Cpp03,
        STLHeader.print               : Standard.Cpp26,
        STLHeader.queue               : Standard.Cpp03,
        STLHeader.random              : Standard.Cpp11,
        STLHeader.ranges              : Standard.Cpp20,
        STLHeader.ratio               : Standard.Cpp11,
        STLHeader.regex               : Standard.Cpp11,
        STLHeader.scoped_allocator    : Standard.Cpp11,
        STLHeader.semaphore           : Standard.Cpp20,
        STLHeader.set                 : Standard.Cpp03,
        STLHeader.setjmp_h            : Standard.Cpp03,
        STLHeader.shared_mutex        : Standard.Cpp17,
        STLHeader.source_location     : Standard.Cpp20,
        STLHeader.span                : Standard.Cpp20,
        STLHeader.sstream             : Standard.Cpp03,
        STLHeader.stack               : Standard.Cpp11,
        STLHeader.stdatomic_h         : Standard.Cpp11,
        STLHeader.stdbool_h           : Standard.Cpp11,
        STLHeader.stddef_h            : Standard.Cpp03,
        STLHeader.stdexcept           : Standard.Cpp03,
        STLHeader.stdint_h            : Standard.Cpp11,
        STLHeader.stdio_h             : Standard.Cpp03,
        STLHeader.stdlib_h            : Standard.Cpp03,
        STLHeader.stop_token          : Standard.Cpp20,
        STLHeader.streambuf           : Standard.Cpp03,
        STLHeader.string              : Standard.Cpp03,
        STLHeader.string_h            : Standard.Cpp03,
        STLHeader.string_view         : Standard.Cpp17,
        STLHeader.strstream           : Standard.Cpp03,
        STLHeader.system_error        : Standard.Cpp11,
        STLHeader.tgmath_h            : Standard.Cpp11,
        STLHeader.thread              : Standard.Cpp11,
        STLHeader.tuple               : Standard.Cpp11,
        STLHeader.type_traits         : Standard.Cpp11,
        STLHeader.typeindex           : Standard.Cpp11,
        STLHeader.typeinfo            : Standard.Cpp03,
        STLHeader.uchar_h             : Standard.Cpp11,
        STLHeader.unordered_map       : Standard.Cpp11,
        STLHeader.unordered_set       : Standard.Cpp11,
        STLHeader.utility             : Standard.Cpp11,
        STLHeader.valarray            : Standard.Cpp03,
        STLHeader.variant             : Standard.Cpp17,
        STLHeader.vector              : Standard.Cpp03,
        STLHeader.version             : Standard.Cpp17,
        STLHeader.wchar_h             : Standard.Cpp03,
        STLHeader.wctype_h            : Standard.Cpp03
    }
    return dmap[self]


  @staticmethod
  def small_core_header_sample() -> list:
    H = STLHeader
    return [
      H.algorithm,
      H.vector,
      H.memory,
      H.functional,
      H.iostream,
      H.utility,
      H.tuple,
      H.numeric,
      H.chrono,
      H.random ,
      H.type_traits,
      H.unordered_map,
      H.map,
      H.string,
      H.string_view,
      H.fstream
    ]

  @staticmethod
  def core_header_sample() -> list:
      """Return the first dialect containing the standard"""
      return [
        STLHeader.algorithm,
        STLHeader.any,
        STLHeader.array,
        STLHeader.atomic,
        STLHeader.chrono,
        STLHeader.condition_variable,
        STLHeader.deque,
        STLHeader.exception,
        STLHeader.fstream,
        STLHeader.functional,
        STLHeader.initializer_list,
        STLHeader.ios,
        STLHeader.iosfwd,
        STLHeader.iostream,
        STLHeader.istream,
        STLHeader.iterator,
        STLHeader.limits,
        STLHeader.list,
        STLHeader.locale,
        STLHeader.map,
        STLHeader.memory,
        STLHeader.new,
        STLHeader.numeric,
        STLHeader.optional,
        STLHeader.ostream,
        STLHeader.random,
        STLHeader.ratio,
        STLHeader.regex,
        STLHeader.set,
        STLHeader.sstream,
        STLHeader.string,
        STLHeader.string_view,
        STLHeader.strstream,
        STLHeader.system_error,
        STLHeader.thread,
        STLHeader.tuple,
        STLHeader.type_traits,
        STLHeader.typeindex,
        STLHeader.typeinfo,
        STLHeader.unordered_map,
        STLHeader.unordered_set,
        STLHeader.utility,
        STLHeader.valarray,
        STLHeader.variant,
        STLHeader.vector
        ]


class LibcxxInfo(BaseModel):
  name : str
  path : Path
  identifier : Identifier
  is_installed: Optional[bool] = Field(default=False)
  install_flags: Optional[list[str]] = Field(default_factory=list)
  include_paths: list[Path] = Field(default_factory=list)
  library_paths: list[Path] = Field(default_factory=list)
  libraries: list[Path] = Field(default_factory=list)
  supported_dialects: Optional[list[str]] = None

  def abs_include_paths(self):
    return [self.path / i for i in self.include_paths]

  def has_version(self):
    return isinstance(self.identifier, Version)

  def find_header(self, filename):
    for i in self.include_paths:
      full_i = self.path / i
      assert full_i.is_dir()
      possible = full_i / filename
      if possible.is_file():
        return possible
    return None

  def is_libcxx_path(self, p):
    return Path(p).is_relative_to(self.path) or self.is_libcxx_header(p)

  def is_libcxx_header(self, p):

    p = Path(p).absolute()
    abs_includes = [Path(self.path, ii) for ii in self.include_paths]
    return any([p.is_relative_to(a) for a in abs_includes])


  def get_headers(self):
    headers = []
    for i in self.abs_include_paths():
      headers += [h.absolute() for h in Path(i).rglob('*') if h.is_file() and '_LIBCPP' in h.read_text()]
    return list(set(headers))

  def absolute_header_path(self, i):
    for a in self.abs_include_paths():
      test_p = a / i
      if test_p.is_file():
        return test_p
    return Path(i)

  def relative_header_path(self, i):
    assert self.is_libcxx_header(i)
    p = Path(i).absolute()
    abs_includes = [Path(self.path, ii) for ii in self.include_paths]
    for ii in abs_includes:
      test_p = ii / p
      if test_p.is_relative_to(ii):
        return test_p.relative_to(ii)
    assert Path(i).name == i
    return Path(i)

  def include_flags(self, include_flag='-cxx-isystem', root=None):
    if root is None:
      root = self.path
    if self.is_installed and self.install_flags:
      return self.install_flags
    result = ['-nostdinc++', '-Wno-unused-command-line-argument']
    for r in self.include_paths:
      prefix = '' if include_flag == '-I' else ''
      result += [ include_flag , str(Path(root) / r)]
    return result

  def library_flags(self, root=None):
    if root is None:
      root = self.path
    if self.is_installed and self.install_flags:
      return self.install_flags
    result = ['-stdlib=libc++', '-Wno-unused-command-line-argument']
    for r in self.library_paths:
      result += ['-L', str(Path(root) / r), '-Wl,-rpath,' + str(Path(root) / r)]
    return result

  def flags(self, root=None):
    return  self.include_flags(root=root) + self.library_flags(root=root)

  def ld_library_paths(self, root=None):
    if root is None:
      root = self.path
    return [str(Path(root) / l) for l in self.library_paths]

  def __eq__(self, other):
    if isinstance(other, LibcxxInfo):
      return self.path == other.path
    return False

  def __lt__(self, other):
    if not isinstance(other, LibcxxInfo):
      raise RuntimeError('Cannot compare type %s' % type(other))
    return self.identifier < other.identifier

  @staticmethod
  def create_from_info(p):
    p = Path(p).absolute()
    assert p.name == 'info.json'
    obj = json.loads(p.read_text())
    if not obj.get('is_installed', False):
      obj['path'] = p.parent
    else:
      assert Path(obj['path']).is_dir()
    model = LibcxxInfo.model_validate(obj)
    model.check()
    return model

  def check(self):
    assert (self.path / 'info.json').is_file() or self.is_installed
    assert self.install_flags or (self.path / self.include_paths[0]).is_dir()

    #assert (self.path / 'bin').is_dir()

  @staticmethod
  def create_from_path(p):
    p = Path(p).absolute()
    if p.name == 'info.json':
      info = LibcxxInfo.create_from_info(p)
    else:
      info = LibcxxInfo.create_from_install(p)
    return info

  @staticmethod
  def create_from_install(p):
    p = Path(p).absolute()
    args = {'path': p}
    if m := CLANG_TRUNK_RE.match(p.name):
      args['identifier'] = Datestamp.from_match(m)
    elif m := CLANG_VERSIONED_RE.match(p.name):
      args['identifier'] = Version.from_match(m)
    else:
      raise RuntimeError('name %s does not match any regex' % p.name)
    args['name'] = args['identifier'].to_string()
    obj = LibcxxInfo.model_validate(args)

    obj.include_paths = [Path(i) for i in ['include/c++/v1', 'include/x86_64-unknown-linux-gnu/c++/v1'] if (p / i).is_dir()]

    for l in LIBRARY_NAMES:
      obj.libraries += [i for i in p.rglob(f'{l}.*') if i.is_file() or i.is_symlink()]
    obj.libraries = list(set([l.relative_to(p) for l in obj.libraries]))
    obj.library_paths = list(set([i.parent for i in obj.libraries]))
    return obj



class CompilerInfo(BaseModel):
  path : Path = Field(default_factory=lambda: Path(shutil.which('clang++')))
  id: str = Field(default=None)
  compile_flags: list[str] = Field(default_factory=list)
  link_flags: list[str] = Field(default_factory=list)


  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    if not self.id :
      self.id = subprocess.check_output([self.path, '--version'], shell=False)

  def set_enviroment(self):
    os.environ['CXX'] = str(self.path)
    os.environ['CXXFLAGS'] = ' '.join(self.compile_flags)
    os.environ['LDFLAGS'] = ' '.join(self.link_flags)
    return copy.copy(os.environ)


class CompilationDatabaseEntry(BaseModel):
  directory: str|Path = Field(default_factory=os.getcwd)
  arguments: list[str|Path] = Field(default_factory=list)
  file: str|Path
  command: Optional[str|Path]  = None
  output: Optional[str|Path] = None

  def as_database(self):
    db = CompilationDatabase()
    db.add(self)
    return db

class CompilationDatabase(RootModel):
  root: list[CompilationDatabaseEntry] = Field(default_factory=list)

  def add(self, entry):
    self.root.append(entry)
    return self

  def save(self, filename):
    p = Path(filename)
    if p.is_dir():
      p = Path(p / 'compile_commands.json')
    Path(p).write_text(self.model_dump_json(indent=2))
    return self



class Duration(BaseModel):
  microseconds: int

  @property
  def seconds(self):
    return self.microseconds / 1000000.0

  @property
  def milliseconds(self):
    return self.microseconds / 1000.0

  def __str__(self):
    import humanfriendly
    return humanfriendly.format_timespan(self.seconds, )

from enum import Enum

class SIPrefix(Enum):
    YOTTA = 1e24
    ZETTA = 1e21
    EXA = 1e18
    PETA = 1e15
    TERA = 1e12
    GIGA = 1e9
    MEGA = 1e6
    KILO = 1e3
    HECTO = 1e2
    DECA = 1e1
    BASE = 1
    DECI = 1e-1
    CENTI = 1e-2
    MILLI = 1e-3
    MICRO = 1e-6
    NANO = 1e-9
    PICO = 1e-12
    FEMTO = 1e-15
    ATTO = 1e-18
    ZEPTO = 1e-21
    YOCTO = 1e-24

    @staticmethod
    def common_prefixes():
      S = SIPrefix
      return [S.TERA, S.GIGA, S.MEGA, S.KILO, S.CENTI, S.MEGA, S.MICRO, S.MILLI, S.NANO]

    def prefix(self):
      return self.name.lower()

    def __truediv__(self, other):
        if isinstance(other, SIPrefix):
            return self.value / float(other.value)
        else:
            return NotImplemented

# Usage:
def SIType(*, suffix=''):
  def _si_type(cls):
    for c in SIPrefix.common_prefixes():
      def new_fn(nc):
        def fn(obj):
          return cls(value=obj.value * (obj.prefix / nc), prefix=nc)
        return fn
      if c == SIPrefix.BASE:
        if suffix == '':
          continue
        setattr(cls, f'{suffix}', new_fn(c))
      else:
        setattr(cls, f'{c.name.lower()}{suffix}', new_fn(c))
    return cls
  return _si_type

class SIValue(BaseModel):
  value : int|float = Field(default=0)
  prefix : SIPrefix = Field(default=SIPrefix.BASE)

  def to(self, prefix):
    return SIValue(value=self.value * (self.prefix.value / prefix.value), prefix=prefix)


@SIType(suffix='bytes')
class Bytes(SIValue):
  def __init__(self, value=0, prefix=SIPrefix.BASE):
    super().__init__(value=value, prefix=prefix)

  def __int__(self):
    return self.value



class MemoryUsage(BaseModel):
  kilobytes: int


  @property
  def bytes(self):
    return self.kilobytes * (SIPrefix.KILO / SIPrefix.BASE)

  @property
  def gigabytes(self):
    return self.kilobytes * (SIPrefix.KILO / SIPrefix.GIGA)

  @property
  def megabytes(self):
    return self.kilobytes / 1000.0

  def __str__(self):
    import humanfriendly
    return humanfriendly.format_size(self.bytes, binary=True)

class DebugOpts(Enum):
  OFF = '-g0'
  ON = '-g'

  def pathkey(self):
    if self == DebugOpts.OFF:
      return "debug_off"
    elif self == DebugOpts.ON:
      return "debug_on"

class OptimizerOpts(Enum):
  O0 = '-O0'
  O1 = '-O1'
  O2 = '-O2'
  O3 = '-O3'

  def pathkey(self):
    return self.value.replace('-', '')

class TestInputs(str, Enum):
  vector = 'instantiation/vector.cpp'
  shared_ptr = 'instantiation/shared_ptr.cpp'
  algorithm = 'instantiation/algorithm.cpp'
  unordered_map = 'instantiation/unordered_map.cpp'
  def path(self):
    return LIBCXX_INPUTS_ROOT / self.value

  def pathkey(self):
    return self.value

  def __hash__(self):
    return hash(self.path().read_text())


class TimeWindowSize(Enum):
  DAYS = 'day',
  WEEKS = 'week'
  MONTHS = 'month'
  YEARS = 'year'


class TimeWindow(BaseModel):
  size : TimeWindowSize = Field(default=TimeWindowSize.WEEKS)
  weeks_ago: int


