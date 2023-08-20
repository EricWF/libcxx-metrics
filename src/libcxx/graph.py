import importlib

import plotly
import plotly.graph_objs as go
import pandas as pd
import tqdm

import asyncio
from libcxx.job import *
from libcxx.jobs import *
from jinja2 import Environment, FileSystemLoader

STD_DIALECTS = Standard.between(Standard.Cpp14, Standard.Cpp23)

TEMPLATE_DIR = Path(__file__).absolute().parent / 'templates'
file_loader = FileSystemLoader(TEMPLATE_DIR)
jinja_env = Environment(loader=file_loader)


def create_all_jobs():
  st_jobs = StdSymbolsJob.jobs()
  st_jobs += IncludeSizeJob.jobs()
  st_jobs += BinarySizeJob.jobs()
  st_jobs += CompilerMetricsJob.jobs()
  st_jobs += CompilerMetricsTestSourceJob.jobs()
  import random
  random.seed(random.getrandbits(128))
  random.shuffle(st_jobs)
  return st_jobs


def prepopulate():

  #prepopulate_jobs_by_running_threaded(create_all_jobs())
  aprepopulate()
  # prepopulate_jobs_by_running_singlethread(st_jobs)

def aprepopulate():
  jobs = create_all_jobs()
  asyncio.run(async_run_jobs(jobs))

def generate_json(cls, std, getter, ylabel, title):
  versions = cls.job_inputs()['libcxx']
  versions.sort()
  plotkeys = cls.plotkeys()
  data = {
      'version': [v.value for v in versions]
  }
  dp = lambda **kwargs: getter(
    cls.create_job(**kwargs).db_get(allow_missing=False))

  for h in plotkeys:
    data[h.name] = list(
        [dp(libcxx=v, standard=std, **h.key_parts) for v in versions])

  # Convert data to DataFrame
  df = pd.DataFrame(data)
  traces = []
  for h in plotkeys:
    # Create a trace
    traces += [go.Scatter(
        x=df['version'],
        y=df[h.name],
        mode='lines+markers',
        name=h.name
    )]

  graphJSON = json.dumps(traces, cls=plotly.utils.PlotlyJSONEncoder)

  output = {
      "title": title + f': {std.value}',
      'xlabel': 'Versions',
      "ylabel": ylabel,
      "data": traces  # This line includes the Plotly JSON in the output
  }
  return output



def generate_json_file(output_path):
  output_path = Path(output_path).absolute()
  plotkeys = []

  def mkname(key, std):
    return f'{key}/{std.value}'

  all_data = {}

  for s in STD_DIALECTS:
    data = {
        mkname('include/time', s): generate_json(CompilerMetricsJob, s, lambda
            x: x.compute_average().total_execution_time.milliseconds,
                                                 ylabel='milliseconds',
                                                 title='Total Time'),
        mkname('include/usr-time', s): generate_json(CompilerMetricsJob, s,
                                                     lambda
            x: x.compute_average().user_execution_time.milliseconds,
                                                     ylabel='milliseconds',
                                                     title='User Time'),
        mkname('include/memory', s): generate_json(CompilerMetricsJob, s, lambda
            x: x.compute_average().peak_memory_usage.kilobytes,
                                                   ylabel='Kilobytes',
                                                   title='Peak Memory Usage'),
        mkname('instantiate/time', s): generate_json(
          CompilerMetricsTestSourceJob, s, lambda
              x: x.compute_average().total_execution_time.milliseconds,
          ylabel='milliseconds', title='Total Time'),
        mkname('instantiate/usr-time', s): generate_json(
          CompilerMetricsTestSourceJob, s, lambda
              x: x.compute_average().user_execution_time.milliseconds,
          ylabel='milliseconds', title='User Time'),
        mkname('instantiate/memory', s): generate_json(
          CompilerMetricsTestSourceJob, s, lambda
              x: x.compute_average().peak_memory_usage.kilobytes,
          ylabel='Kilobytes',
          title='Peak Memory Usage'),

        mkname('include_size', s): generate_json(IncludeSizeJob, s,
                                                 lambda x: x.line_count,
                                                 ylabel='LOC',
                                                 title='Preprocessed LOC', ),
        mkname('symbol_count', s): generate_json(StdSymbolsJob, s,
                                                 lambda x: x.symbol_count,
                                                 ylabel='# Symbols',
                                                 title='Visible Symbols'),
        mkname('binary_size', s): generate_json(BinarySizeJob, s,
                                                lambda x: x.bytes,
                                                ylabel='bytes',
                                                title='Object Size')
    }
    all_data.update(data)
  output_path.write_text(
    json.dumps(all_data, indent=2, cls=plotly.utils.PlotlyJSONEncoder))
  return all_data

if __name__ == '__main__':

  init_db()
  prepopulate()
  generate_json_file('/tmp/data.json')
