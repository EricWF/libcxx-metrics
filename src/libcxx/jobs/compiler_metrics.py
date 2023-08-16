from pydantic import BaseModel
from elib.libcxx.types import *
from elib.libcxx.job import *
import shutil
import subprocess

class CompilerMetrics(BaseModel):
  filename: str
  output_filename: str
  total_execution_time: Duration
  user_execution_time: Duration
  peak_memory_usage: MemoryUsage

  @staticmethod
  def create_empty():
    dur0 = Duration(microseconds=0)
    return CompilerMetrics(filename='', output_filename='', total_execution_time=dur0, user_execution_time=dur0, peak_memory_usage=MemoryUsage(kilobytes=0))


class CompilerMetricsList(RootModel):
  root : list[CompilerMetrics] = Field(default_factory=list)

  def append(self, obj : CompilerMetrics):
    self.root.append(obj)
    self.recompute_average()

  def __len__(self):
    return len(self.root)

  def runs(self):
    return list(self.root)

  def recompute_average(self):
    runs = self.root
    N = len(self.root)
    if N == 0:
      return
    NF = float(N)
    ex_time = sum([r.total_execution_time.microseconds for r in runs]) / NF
    usr_time = sum([r.user_execution_time.microseconds for r in runs]) / NF
    mem = sum([r.peak_memory_usage.kilobytes for r in runs]) / NF
    return CompilerMetrics.model_validate({
        'filename': runs[0].filename,
        'output_filename': runs[0].output_filename,
        'total_execution_time': {
            'microseconds': int(ex_time)
        },
        'user_execution_time': {
            'microseconds': int(usr_time)
        },
        'peak_memory_usage': {
            'kilobytes': int(mem)
        }
    })



class CompilerMetricsJob(LibcxxJob):
  class Key(JobKey):
    libcxx: LibcxxVersion
    standard: Standard
    header: STLHeader

  class Output(CompilerMetricsList):
    pass

  def run(self):
    input_file = self.tmp_file('input.cpp',
                               '#include <%s>\nint main() {\n}\n' % self.key.header.value)

    output_file = self.output_file('usage.txt')
    cmd = [shutil.which('clang++'), '-o', '/dev/null', '-c'] + \
          [self.key.standard.flag()] + self.libcxx.include_flags() + \
          [f'-fproc-stat-report={output_file}'] + \
          ['-xc++', str(input_file)]

    runs = CompilerMetricsJob.Output()

    RUNS = 10
    for i in range(0, RUNS):
      out = subprocess.check_output(cmd).decode('utf-8').strip()
      csv = [p.strip() for p in output_file.read_text().strip().splitlines()[0].split(',') if p.strip()]
      tmp_out = CompilerMetrics.model_validate({
          'filename': csv[0],
          'output_filename': csv[1],
          'total_execution_time': {
              'microseconds': int(csv[2])
          },
          'user_execution_time': {
              'microseconds': int(csv[3])
          },
          'peak_memory_usage': {
              'kilobytes': int(csv[4])
          }
      })
      runs.append(tmp_out)
    return self.key, runs

