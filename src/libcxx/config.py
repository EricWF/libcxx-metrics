from pathlib import Path

LIBCXX_METRICS_ROOT =  Path(__file__).absolute().parent.parent.parent
assert LIBCXX_METRICS_ROOT.is_dir()
LIBCXX_VERSIONS_ROOT = LIBCXX_METRICS_ROOT / 'libcxx-versions'
LIBCXX_INPUTS_ROOT = LIBCXX_METRICS_ROOT / 'inputs'
assert LIBCXX_VERSIONS_ROOT.is_dir()
