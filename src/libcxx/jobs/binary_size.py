from libcxx.types import *
from libcxx.job import *
import subprocess
import shutil

class BinarySizeJob(LibcxxJob):
  class Key(JobKey):
    libcxx: LibcxxVersion
    standard: Standard
    header: STLHeader

  class Output(BaseModel):
    size: int
    debug_size: int

  def run(self):
    input_file = self.tmp_file('input.cpp',
                               '#include <%s>\nint main() {\n}\n' % self.key.header.value)


    cmd = [shutil.which('clang++'),  self.key.standard.flag(), '-E'] + self.libcxx.include_flags() + ['-xc++', str(input_file)]
    out = subprocess.check_output(cmd).decode('utf-8').strip()
    lines = [l.strip() for l in out.splitlines() if l.strip().startswith('#')]
    return self.key, BinarySizeJob.Output(line_count=len(lines))
