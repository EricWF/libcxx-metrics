from libcxx.job import *
from libcxx.types import *
import subprocess
import shutil


class IncludeSizeJob(LibcxxJob):
  class Key(JobKey):
    libcxx: LibcxxVersion
    standard: Standard
    header: STLHeader

  class Output(BaseModel):
    line_count: int
    size_in_bytes: int

  def run(self):
    input_file = self.tmp_file('input.cpp',
                               '#include <%s>\nint main() {\n}\n' % self.key.header.value)


    cmd = [shutil.which('clang++'),  self.key.standard.flag(), '-E'] + \
            self.libcxx.include_flags() + ['-xc++', str(input_file)]
    out = subprocess.check_output(cmd).decode('utf-8').strip()
    def want_line(l):
      l = l.strip()
      if l.startswith('#') or not l:
        return False
      return True
    lines = [l.strip() for l in out.splitlines() if want_line(l)]

    return IncludeSizeJob.Output(line_count=len(lines), size_in_bytes=len(out))

