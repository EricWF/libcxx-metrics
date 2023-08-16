from elib.libcxx.types import *

class LibcxxInfoInternal(LibcxxInfo):
  def copy(self, output_dir):
    raise RuntimeError('Not implemented')

  def _env_file(self):
    return f'''
#!/usr/bin/env bash
EBIN_DIR=$( cd -- "$( dirname -- "${{BASH_SOURCE[0]}}" )" &> /dev/null && pwd )
EBIN_DIR=$(realpath $EBIN_DIR)
set -o allexport
ECLANG_ROOT=$(realpath $EBIN_DIR/..)
ECXX=$ECLANG_ROOT/bin/eclang++
ECXXFLAGS=({' '.join('%s' % i for i in self.include_flags(root="$ECLANG_ROOT"))})
ELDFLAGS=({' '.join('%s' % i for i in self.library_flags(root="$ECLANG_ROOT"))})
export ELD_LIBRARY_PATH={':'.join(self.ld_library_paths(root="$ECLANG_ROOT"))}
'''.strip()

  def create_env_file(self):
    env_script = Path(self.path / 'bin' / 'env.sh')
    env_script.write_text(self._env_file())
    os.system(f'chmod +x {env_script}')

    run_env_template = self._env_file() + '\n' + '''
export CXX=$ECLANG_ROOT/bin/eclang++
export CXXFLAGS=$ECXXFLAGS
export LDFLAGS=$ELDFLAGS
export LD_LIBRARY_PATH=$ELD_LIBRARY_PATH
'''.strip()
    activate_script = Path(self.path / 'bin' / 'activate.sh')
    activate_script.write_text(run_env_template)
    os.system(f'chmod +x {activate_script}')

  def create_compiler_wrapper(self):
    script = self._env_file() + '\n' + '''
CXX=${CXX:-clang++}
BASE_CXX="$(basename $CXX)"
if [[ $BASE_CXX == "eclang++" ]]; then
  CXX=clang++
fi
unset CXXFLAGS LDFLAGS
echo $CXX ${ECXXFLAGS[@]} ${ELDFLAGS[@]} "$@"
$CXX ${ECXXFLAGS[@]} ${ELDFLAGS[@]} "$@"
'''.strip()
    out_path = Path(self.path, 'bin')
    out_path.mkdir(exist_ok=True)

    op = Path(out_path / 'eclang++')
    op.write_text(script.strip())
    os.system(f'chmod +x {op}')

  def create_test_inputs(self):
    out_path = Path(self.path, 'inputs')
    out_path.mkdir(exist_ok=True)
    include_tests_path = out_path / 'include_tests'
    include_tests_path.mkdir(exist_ok=True)
    output = {}
    for i in LIBCXX_COMMON_HEADERS:
      op = Path(out_path / i)
      op.write_text('#include <{i}>\nint main() {{\n}}\n'.format(i=i))
      output[i] = op


  def tar(self, output_dir=None):
    return stage_libcxx(self, output_dir=output_dir)

  @staticmethod
  def untar(tarball, root=None):
    tarball = Path(tarball)
    dirname = tarball.with_suffix('').name
    if root is None:
      root = Path(f'/tmp/{dirname}')
      root.mkdir(exist_ok=True)
    else:
      root = Path(root)

    assert tarball.is_file()
    rich.print(f'Extracting {tarball.name} to {root}')
    ret = subprocess.run([shutil.which('tar'), '-xzvf', f'{tarball}', '--strip-components=1', '-C',  f'{root}'])



LIBCXX_COMMON_HEADERS = ['vector', 'functional', 'memory', 'algorithm', 'type_traits', 'utility',
                         'regex', 'iterator', 'thread', 'iostream', 'algorithm', 'tuple',
                         'forward_list', 'map','unordered_map', 'list', 'chrono', 'random', 'variant']

LIBCXX_INCLUDE_HEADER_SOURCES = {k: Path(f'sources/{k}.cpp') for k in LIBCXX_COMMON_HEADERS}

def create_include_sources(headers, output_dir):
  output_dir = Path(output_dir).absolute()
  output_dir.mkdir(exist_ok=True)
  srcs = {}
  for h in headers:
    op = output_dir / f'{h}.cpp'
    op.write_text(f'#include <{h}>\nint main() {{\n}}\n')
    srcs[h] = str(op)
  return srcs

def stage_libcxx(info : LibcxxInfo, output_dir=None, create_tar=True):
  import tempfile
  tmp_dir = Path(tempfile.mkdtemp(info.name)) if output_dir is None else Path(Path(output_dir) / info.name)
  if not tmp_dir.is_dir():
    tmp_dir.mkdir(exist_ok=True)
  rich.print(f'Using tmp dir {tmp_dir}')
  assert tmp_dir.is_dir()
  for d in info.library_paths:
    Path(tmp_dir / d).mkdir(parents=True, exist_ok=True)
  link_later = []
  for l in info.libraries:
    in_p = info.path / l
    out_p = tmp_dir / l

    if in_p.is_symlink():
      assert in_p.name in ['libc++.so.1', 'libc++abi.so', 'libc++abi.so.1']
      old_dir = Path(os.curdir).absolute()
      os.chdir(out_p.parent)
      ret = os.system(f'ln -s {os.readlink(in_p)} {l.name}')
      os.chdir(old_dir)
    elif in_p.is_file():
      shutil.copyfile(in_p, out_p)


  for d in info.include_paths:
    shutil.copytree(info.path / d, tmp_dir / d)
  oinfo = info.model_copy()
  oinfo.path = tmp_dir
  Path(tmp_dir / 'info.json').write_text(oinfo.model_dump_json(indent=2))
  assert Path(output_dir).is_dir()
  if not create_tar:
    assert output_dir is not None
    return oinfo

  output_dir = Path('/tmp' if output_dir is None else output_dir)

  out = output_dir / f'{info.name}.tar.gz'
  assert out.suffix == '.gz'
  subprocess.run([shutil.which('tar'), '-czvf',  f'{out}',  f'{tmp_dir}/'],  capture_output=True)
  shutil.rmtree(tmp_dir)
  return None
