import asyncio

from libcxx.types import *
from libcxx.db import registry
from libcxx.job import *
import subprocess
import shutil
from types import SimpleNamespace
import asyncio
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

  state : Any = Field(exclude=True, default_factory=SimpleNamespace)

  def setup_state(self):
    self.state.input_file = self.key.input.path()
    self.state.object_file = self.tmp_file('test.o')
    flags = [self.key.debug.value, self.key.optimize.value]
    self.state.cmd = [shutil.which('clang++'), '-c',  self.key.standard.flag()] \
      + self.libcxx.include_flags() + flags  \
      + ['-I', str(LIBCXX_INPUTS_ROOT / 'include')] \
      + ['-o', str(self.state.object_file), '-xc++', str(self.state.input_file)]

  def run(self):
    self.setup_state()
    proc = subprocess.Popen(self.state.cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out,err = proc.communicate()
    assert proc.poll() is not None
    return self.postprocess_output(proc, out)

  async def asrun(self):
    self.setup_state()
    proc = await asyncio.create_subprocess_exec(*self.state.cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
    out, _ = await proc.communicate()
    return  self.postprocess_output(proc, out)

  def postprocess_output(self, proc, out):
    if proc.returncode != 0:
      rich.print(f'Compilation failed for {self.input_file}.name with code {proc.returncode} for invocation:\n  {" ".join(cmd)}')
      rich.print(out.decode('utf-8'))
      return None

    stat = os.stat(self.object_file)
    return BinarySizeJob.Output(bytes=stat.st_size)


if __name__ == '__main__':

  prepopulate_jobs_by_running_threaded(list(BinarySizeJob.jobs()))
