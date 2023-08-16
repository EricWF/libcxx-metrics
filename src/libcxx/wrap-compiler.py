from elib.libcxx.types import LibcxxInfo

def _is_compile_command(args : list[str]):
  for a in args:
    if a in ['-c', '-E', '-xc++']:
      return True
    if Path(a).is_file() and Path(a).suffix in ['.cpp', '.cxx', '.cpp', '.h', '.hpp', '.hxx']

ENV_VAR = 'LIBCXX_VER'
DEFAULT_LIBCXX_VER


