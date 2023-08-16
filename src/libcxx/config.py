from pathlib import Path


LIBCXX_VERSIONS_ROOT = Path(__file__).absolute().parent.parent.parent / 'libcxx-versions'
assert LIBCXX_VERSIONS_ROOT.is_dir()
