#!/usr/bin/env python3
import os
import sys
import json
from pathlib import Path

from dataclasses import dataclass, field
import shlex

BIN_PATH = Path(__file__).absolute().parent
LIBCXX_VERSIONS_ROOT = BIN_PATH.parent / 'libcxx-versions'
LIBCXX_METRICS_ROOT = BIN_PATH.parent
LIBCXX_PYTHON_ROOT = (BIN_PATH.parent / 'src').absolute()
if LIBCXX_PYTHON_ROOT not in sys.path:
  sys.path.append(LIBCXX_PYTHON_ROOT)
from libcxx.types import *




ARGS = sys.argv[1:]


def determine_versions():
  version = None
  for idx, a in enumerate(ARGS):
    if '--libcxx=' in a:
      version = a[len('--libcxx='):]
      del ARGS[idx]
      break
  if version is None:
    version = os.environ['LIBCXX_VERSION']
    if version is None:
      print('--libcxx must be passed or LIBCXX_VERSION must be set')
      sys.exit(1)
  return version.split(',')


def load_version(v):
    VERSION_LIST = [lv for lv in LibcxxVersion]

    def test_it(tv):
      if v in VERSION_LIST:
        return VERSION_LIST[VERSION_LIST.index(v)].load()
      sp = LIBCXX_VERSIONS_ROOT / tv / 'info.json'
      if sp.is_file():
        return LibcxxInfo.create_from_path(sp)
      return None

    try_formats = ['{v}', 'v{v}', '{v}.0.1', '{v}.0.0', '{v}.1.0', '{v}.0', '{v}.1']
    for tf in try_formats:
      fstr = tf.format(v=v)
      if res := test_it(fstr):
        return (v, res)
    raise RuntimeError(f'No such version for {v}')

VERSIONS = [load_version(v) for v in determine_versions()]


def format_arg(a, name):
  if '{libcxx}' not in a:
    return a
  return a.replace('{libcxx}', name)

COMPILER = 'clang++'
if 'CXX' in os.environ and 'eclang' not in os.environ['CXX']:
  COMPILER = os.environ['CXX']
COMPILER = shutil.which(COMPILER)
assert Path(COMPILER).absolute() != Path(__file__).absolute()


@dataclass
class Runner:
  libcxx: LibcxxVersion
  name: str
  args: list[str]
  compiler: str = field(default_factory=lambda: COMPILER)
  command: list[str] = field(default_factory=list)
  verbose: Optional[bool] = field(default=False)

  def build_cmd(self):
    args =  [ format_arg(a, self.name) for a in self.args ]
    args = [COMPILER] + args + ['-I', str(LIBCXX_METRICS_ROOT / 'inputs/include')]

    compile_only = '-c' in args or '-E' in args or '-fsyntax-only' in args
    self.verbose = '-v' in args or '-ev' in args
    if '-ev' in args:
      del args[args.index('-ev')]
    args += self.libcxx.include_flags()
    if not compile_only:
      args += self.libcxx.library_flags()
    return list(args)


  @staticmethod
  def create(*, args, name, libcxx,  compiler=COMPILER):
    r =  Runner(compiler=compiler, name=name, args=list(args), libcxx=libcxx)
    r.command = r.build_cmd()
    return r


  def become_compile_command(self):
    if self.verbose:
      print(' '.join(self.command))
    return os.execvp(self.compiler, self.command)

  def compile(self, exit_non_zero=True):
    if self.verbose:
      print(' '.join(self.command))
    ret = os.system(shlex.join(self.command))
    if exit_non_zero and ret != 0:
      sys.exit(ret)
    return ret

def check_versions_for_subs():
  if len(VERSIONS) == 1:
    return
  for a in ARGS:
    if '{libcxx}' in a:
      return
  print('Multiple libc++ versions requested, but no substitution present in arguments (use {libcxx} to expand)', file=sys.stderr)
  sys.exit(1)

def main():
  single_run = len(VERSIONS) == 1

  for name,libcxx in VERSIONS:
    r = Runner.create(args=ARGS, compiler=COMPILER, libcxx=libcxx, name=name)
    if single_run:
      return r.become_compile_command()
    else:
      r.verbose = True
      r.compile(exit_non_zero=True)


if __name__ == '__main__':
  main()


