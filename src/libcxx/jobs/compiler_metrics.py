from pydantic import BaseModel
from libcxx.types import *
from libcxx.job import *
import shutil
import subprocess
from libcxx.db import registry
from types import SimpleNamespace as Namespace

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


class CompilerMetricsList(JobOutput):
  runs : list[CompilerMetrics] = Field(default_factory=list)

  def append(self, obj : CompilerMetrics):
    self.runs.append(obj)

  def __len__(self):
    return len(self.runs)



  def extend(self, other):
    if not isinstance(other, CompilerMetricsList):
      raise RuntimeError("Bad type: %s" % type(other))
    self.runs.extend(other.runs)

  def compute_average(self):
    runs = self.runs
    N = len(self.runs)
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


@registry.registered
class CompilerMetricsJob(LibcxxJob):
  class Meta:
    repeatable : bool = True
    runs_per_repeat : int = 250

  @registry.registered
  class Key(JobKey):
    libcxx: LibcxxVersion
    standard: Standard
    header: STLHeader

  @registry.registered
  class Output(CompilerMetricsList):
    pass



  input_file : Path = Field(exclude=True, default_factory=Path)
  compiler: str = Field(exclude=True, default_factory=lambda: shutil.which('clang++'))
  @model_validator(mode='after')
  def validate_state(self):
    if hasattr(self.key, 'header'):
      self.input_file = Path(self.tmp_file('input.cpp',
                               '#include <%s>\nint main() {\n}\n' % self.key.header.value))
    elif hasattr(self.key, 'input'):
      self.input_file = Path(self.key.input.path())
    assert self.compiler == shutil.which('clang++')
    return self


  def make_cmd(self, output_file):
     return [self.compiler, '-o', '/dev/null', '-c'] + \
          [self.key.standard.flag()] + self.libcxx.include_flags() + \
          ['-I', LIBCXX_INPUTS_ROOT / 'include'] + \
          [f'-fproc-stat-report={output_file}'] + \
          ['-xc++', str(self.input_file)]

  def run(self, runs=1):
    return self.run_impl(runs=runs)

  def run_impl(self, runs=1):
    output = self.output_type().model_validate({'hash_value': self.hash_value()})
    with self.tmp_file_guard('results.txt') as output_filename:
      cmd = self.make_cmd(output_filename)
      for i in range(0, runs):
        out = subprocess.check_output(cmd).decode('utf-8').strip()
        csv = [p.strip() for p in output_filename.read_text().strip().splitlines()[0].split(',') if p.strip()]
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
        output.append(tmp_out)
    return output


@registry.registered
class CompilerMetricsTestSourceJob(CompilerMetricsJob):
  @registry.registered
  class Key(JobKey):
    libcxx: LibcxxVersion
    standard: Standard
    input: TestInputs

  @registry.registered
  class Output(CompilerMetricsList):
    pass

  def run(self, runs=1):
    return self.run_impl(runs=runs)
