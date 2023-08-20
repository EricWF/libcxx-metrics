from pathlib import Path
import os

LIBCXX_METRICS_ROOT =  Path(__file__).absolute().parent.parent.parent
assert LIBCXX_METRICS_ROOT.is_dir()
LIBCXX_VERSIONS_ROOT = LIBCXX_METRICS_ROOT / 'libcxx-versions'
LIBCXX_INPUTS_ROOT = LIBCXX_METRICS_ROOT / 'inputs'
assert LIBCXX_VERSIONS_ROOT.is_dir()

LLVM_PROJECT_ROOT = Path(os.path.expanduser('~/llvm-project/'))
if not LLVM_PROJECT_ROOT.is_dir():
  print('Failed to find LLVM project root to use...')
  import sys
  sys.exit(1)

