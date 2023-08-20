import asyncio

from libcxx.job import *
from libcxx.types import *
import subprocess
import shutil
from libcxx.db import registry
from types import SimpleNamespace

class IncludeSizeJob(LibcxxJob):
  @registry.registered
  class Key(JobKey):
    libcxx: LibcxxVersion
    standard: Standard
    header: STLHeader

  @registry.registered
  class Output(BaseModel):
    line_count: int
    size_in_bytes: int

  state : Any = Field(exclude=True, default_factory=SimpleNamespace)

  @model_validator(mode='after')
  def setup_state(self):
    self.state.input_file = self.tmp_file('input.cpp',
                               '#include <%s>\nint main() {\n}\n' % self.key.header.value)


    self.state.cmd = [shutil.which('clang++'),  self.key.standard.flag(), '-E'] + \
            self.libcxx.include_flags() + ['-xc++', str(self.state.input_file)]
    return self

  def postprocess_output(self, out):
    out = out.decode('utf-8').strip()
    def want_line(l):
      l = l.strip()
      if l.startswith('#') or not l:
        return False
      return True
    lines = [l.strip() for l in out.splitlines() if want_line(l)]

    return IncludeSizeJob.Output(line_count=len(lines), size_in_bytes=len(out))

  def run(self):
    out = subprocess.check_output(self.state.cmd)
    return self.postprocess_output(out)


  async def arun(self):
    process = await asyncio.create_subprocess_exec(*self.state.cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
    stdout, _ = await process.communicate()
    if process.returncode != 0:
      raise RuntimeError('Process %s failed with %s \nstdout:\n%s\n' % (self.cmd, process.returncode,
      stdout.decode('utf-8')))
    return self.postprocess_output(stdout)
