#!/usr/bin/env python3
import os
import sys
import json
from pathlib import Path

BIN_PATH = Path(__file__).absolute().parent
LIBCXX_VERSIONS_ROOT = BIN_PATH.parent / 'libcxx-versions'
LIBCXX_METRICS_ROOT = BIN_PATH.parent

sys.path.append(str(LIBCXX_METRICS_ROOT / 'src'))
from libcxx.types import *

VERSION = os.environ['LIBCXX_VERSION']
if VERSION is None:
  print('LIBCXX_VERSION must be set')

def load_version():
  v = VERSION
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
      return res
  raise RuntimeError(f'No such version for {v}')


libcxx = load_version()

COMPILER = 'clang++'
if 'CXX' in os.environ:
  COMPILER = os.environ['CXX']
COMPILER = shutil.which(COMPILER)

def main():
  args = sys.argv[1:]
  args = [COMPILER] + args + ['-I', str(LIBCXX_METRICS_ROOT / 'inputs/include')]
  compile_only = '-c' in args or '-E' in args or '-fsyntax-only' in args
  verbose = '-v' in args or '-ev' in args
  if '-ev' in args:
    del args[args.index('-ev')]
  args += libcxx.include_flags()
  if not compile_only:
    args += libcxx.library_flags()
  if verbose:
    print(' '.join(args))
  return os.execvp(COMPILER, args)

if __name__ == '__main__':
  main()


