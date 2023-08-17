from libcxx.types import *
from libcxx.db import registry
from libcxx.job import *
import subprocess
import shutil

@registry.registered
class BinarySizeJob(LibcxxJob):
  @registry.registered
  class Key(JobKey):
    libcxx: LibcxxVersion
    standard: Standard
    input: TestInputs
    debug: DebugOpts
    optimize: OptimizerOpts

  @registry.registered
  class Output(BaseModel):
    bytes: int



  def run(self):
    input_file = self.key.input.path()
    output_file = self.tmp_file('test.o')
    flags = [self.key.debug.value, self.key.optimize.value]
    cmd = [shutil.which('clang++'), '-c',  self.key.standard.flag()] \
      + self.libcxx.include_flags() + flags  \
      + ['-I', str(LIBCXX_INPUTS_ROOT / 'include')] \
      + ['-o', str(output_file), '-xc++', str(input_file)]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out,err = proc.communicate()
    assert proc.poll() is not None
    if proc.returncode != 0:
      rich.print(f'Compilation failed for {input_file}.name with code {proc.returncode} for invocation:\n  {" ".join(cmd)}')
      rich.print(out.decode('utf-8'))
      return None

    stat = os.stat(output_file)
    return BinarySizeJob.Output(bytes=stat.st_size)


if __name__ == '__main__':

  prepopulate_jobs_by_running_threaded(list(BinarySizeJob.jobs()))
