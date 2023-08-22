import importlib

import plotly
import plotly.graph_objs as go
import pandas as pd
import tqdm
import rich.progress

if __name__ == '__main__':
  from libcxx.jobs import *
import asyncio
from libcxx.job import *
from libcxx.jobs.git_stats import *
from libcxx.db import init_db
from jinja2 import Environment, FileSystemLoader

STD_DIALECTS = Standard.between(Standard.Cpp14, Standard.Cpp23)

TEMPLATE_DIR = Path(__file__).absolute().parent / 'templates'
file_loader = FileSystemLoader(TEMPLATE_DIR)
jinja_env = Environment(loader=file_loader)


def prepopulate():
  jobs = LibcxxJob.all_jobs()
  prepopulate_jobs_by_running_threaded(jobs)


def aprepopulate():
  jobs = LibcxxJob.all_jobs()
  asyncio.run(async_run_jobs(jobs))


class GraphDefinition(BaseModel):
  title: str
  x_label: str
  y_label: str
  data: list[go.Scatter] = Field(default_factory=list)
  model_config = {'arbitrary_types_allowed': True}


def generate_json(cls, *, x_key, x_label, x_values, key_parts, getter, y_label,
    title):
  x_values.sort()
  plotkeys = cls.plotkeys()
  data = {
      x_label: [x.value for x in x_values]
  }
  dp = lambda **kwargs: getter(
      cls.create_job(**kwargs).db_get(allow_missing=False))

  for h in plotkeys:
    data[h.name] = list(
        [dp(**{x_key: v}, **key_parts, **h.key_parts) for v in x_values])

  # Convert data to DataFrame
  df = pd.DataFrame(data)
  traces = []
  for h in plotkeys:
    # Create a trace
    traces += [go.Scatter(
        x=df[x_label],
        y=df[h.name],
        mode='lines+markers',
        name=h.name
    )]

  return GraphDefinition.model_validate({
      "title": title,
      'x_label': x_label,
      "y_label": y_label,
      "data": traces  # This line includes the Plotly JSON in the output
  })


class GraphStore(RootModel):
  root: dict[str, GraphDefinition] = Field(default_factory=dict)

  def __getitem__(self, item):
    return self.root[item]

  def __setitem__(self, key, value):
    return self.root.__setitem__(key, value)

  def update(self, other):
    if isinstance(other, GraphStore):
      other = other.root
    self.root.update(other)

  def dump_plotly_json(self):
    return json.dumps(self.model_dump(), cls=plotly.utils.PlotlyJSONEncoder)

class ArgPack:
  def __init__(self, *args, **kwargs):
    self.args = list(args)
    self.kwargs = dict(kwargs)
  
  def __call__(self, fn):
    return fn(*self.args, **self.kwargs)
  

def generate_json_file(output_path):

  all_data = GraphStore()
  def mk_data(name_prefix, cls,standard, getter, y_label, title):
      title = title + f' {standard.value}'
      key_name = f'{name_prefix}/{standard.value}'
      ret = generate_json(cls, x_label='version', x_key='libcxx',
                          x_values=cls.job_inputs()['libcxx'],
                          key_parts={'standard': standard}, getter=getter,
                          y_label=y_label,
                          title=title)
      all_data[key_name] = ret
  to_do = []
  for s in STD_DIALECTS:
    to_do += [
      ArgPack('include/time', CompilerMetricsJob, s, lambda
          x: x.compute_average().total_execution_time.milliseconds,
              y_label='milliseconds',
              title='Total Time'),
      ArgPack('include/usr-time', CompilerMetricsJob,
              s, lambda
                  x: x.compute_average().user_execution_time.milliseconds,
              y_label='milliseconds',
              title='User Time'),
      ArgPack('include/memory', CompilerMetricsJob, s, lambda
          x: x.compute_average().peak_memory_usage.kilobytes,
              y_label='Kilobytes',
              title='Peak Memory Usage'),
      ArgPack('instantiate/time',
              CompilerMetricsTestSourceJob, s, lambda
                  x: x.compute_average().total_execution_time.milliseconds,
              y_label='milliseconds', title='Total Time'),
      ArgPack('instantiate/usr-time',
              CompilerMetricsTestSourceJob, s, lambda
                  x: x.compute_average().user_execution_time.milliseconds,
              y_label='milliseconds', title='User Time'),
      ArgPack('instantiate/memory',
              CompilerMetricsTestSourceJob, s, lambda
                  x: x.compute_average().peak_memory_usage.kilobytes,
              y_label='Kilobytes',
              title='Peak Memory Usage'),
      ArgPack('include_size', IncludeSizeJob,
              s, lambda x: x.line_count,
              y_label='LOC',
              title='Preprocessed LOC'),
      ArgPack('symbol_count', StdSymbolsJob,
              s, lambda x: x.symbol_count,
              y_label='# Symbols',
              title='Visible Symbols'),
      ArgPack('binary_size', BinarySizeJob,
              s, lambda x: x.bytes,
              y_label='bytes',
              title='Object Size')
    ]
  for a in rich.progress.track(to_do, description='Generating graphs...'):
    a(mk_data)

  output_path = Path(output_path).absolute()
  rich.print(f'Writing data to {output_path}')
  output_path.write_text(
      json.dumps(all_data.model_dump(), cls=plotly.utils.PlotlyJSONEncoder))
  return all_data


if __name__ == '__main__':
  init_db()
  if '--run' in sys.argv or '--rerun' in sys.argv:
    prepopulate()
  generate_json_file('/tmp/data.json')
