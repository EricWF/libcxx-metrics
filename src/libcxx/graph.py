import importlib

import plotly
import plotly.graph_objs as go
import pandas as pd
import tqdm
from libcxx.job import *
from libcxx.jobs import *
from jinja2 import Environment, FileSystemLoader

STD_DIALECTS = Standard.between(Standard.Cpp11, Standard.Cpp23)

TEMPLATE_DIR = Path(__file__).absolute().parent / 'templates'
file_loader = FileSystemLoader(TEMPLATE_DIR)
jinja_env = Environment(loader=file_loader)


def prepopulate():
  mp_jobs = StdSymbolsJob.jobs()
  mp_jobs += IncludeSizeJob.jobs()
  mp_jobs += BinarySizeJob.jobs()
  prepopulate_jobs_by_running_threaded(mp_jobs)
  st_jobs = CompilerMetricsJob.jobs()
  st_jobs += CompilerMetricsTestSourceJob.jobs()
  prepopulate_jobs_by_running_threaded(st_jobs)

  #prepopulate_jobs_by_running_singlethread(st_jobs)



def generate_json(cls, std, getter, ylabel, title):
  versions = cls.job_inputs()['libcxx']
  versions.sort()
  plotkeys = cls.plotkeys()
  data = {
      'version': [v.value for v in versions]
  }
  dp = lambda **kwargs: getter(cls.create_job(**kwargs).db_get(allow_missing=False))

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

def generate_graph(cls, std, getter, ylabel, title, plotkeys : list[PlotKey]):
  versions = cls.job_inputs()['libcxx']


  data = {
      'version': [v.value for v in versions]
  }
  dp = lambda **kwargs: getter(cls.create_job(**kwargs).db_get(allow_missing=False))

  for pc in plotkeys:
    data[pc.name] = list(
        [dp(libcxx=v, standard=std, **pc.key_parts) for v in versions])

  # Convert data to DataFrame
  df = pd.DataFrame(data)
  traces = []
  for h in plotkeys:
    # Create a trace
    traces += [go.Scatter(
        x=df['version'],
        y=df[h.name],
        mode='lines+markers',
        name=h.value
    )]

  graphJSON = json.dumps(traces, cls=plotly.utils.PlotlyJSONEncoder)
  template = jinja_env.get_template('single-graph.html')
  return template.render(title=title + f': {std.value}', ylabel=ylabel,
                         graphJSON=graphJSON)


def symbols_page(std=17):
  obj = generate_graph(StdSymbolsJob, Standard.convert(std),
                       lambda x: x.symbol_count, ylabel='# Symbols',
                       title='Visible Symbols')
  return obj


def includes_page(std=17):
  if std == 17:
    s = Standard.Cpp17
  return generate_graph(IncludeSizeJob, Standard.convert(std),
                        lambda x: x.line_count, ylabel='LOC',
                        title='Preprocessed LOC')


def memory_page(std=17):
  return generate_graph(CompilerMetricsJob, Standard.convert(std), lambda
      x: x.recompute_average().peak_memory_usage.kilobytes, ylabel='Kilobytes',
                        title='Peak Memory Usage')


def total_time_page(std=17):
  return generate_graph(CompilerMetricsJob, Standard.convert(std), lambda
      x: x.recompute_average().total_execution_time.milliseconds,
                        ylabel='milliseconds', title='Total Time')


def usr_time_page(std=17):
  return generate_graph(CompilerMetricsJob, Standard.convert(std), lambda
      x: x.recompute_average().user_execution_time.milliseconds,
                        ylabel='milliseconds', title='User Time')


def generate_json_file(output_path):
  output_path = Path(output_path).absolute()
  plotkeys = []
  def mkname(key, std):
    return f'{key}/{std.value}'
  all_data = {}

  for s in STD_DIALECTS:
    data = {
      mkname('include/time', s): generate_json(CompilerMetricsJob, s, lambda
        x: x.recompute_average().total_execution_time.milliseconds,
                          ylabel='milliseconds', title='Total Time'),
      mkname('include/usr-time', s): generate_json(CompilerMetricsJob, s, lambda
        x: x.recompute_average().user_execution_time.milliseconds,
                          ylabel='milliseconds', title='User Time'),
      mkname('include/memory', s): generate_json(CompilerMetricsJob, s, lambda
        x: x.recompute_average().peak_memory_usage.kilobytes, ylabel='Kilobytes',
                          title='Peak Memory Usage'),
      mkname('instantiate/time', s): generate_json(CompilerMetricsTestSourceJob, s, lambda
        x: x.recompute_average().total_execution_time.milliseconds,
                          ylabel='milliseconds', title='Total Time'),
      mkname('instantiate/usr-time', s): generate_json(CompilerMetricsTestSourceJob, s, lambda
        x: x.recompute_average().user_execution_time.milliseconds,
                          ylabel='milliseconds', title='User Time'),
      mkname('instantiate/memory', s): generate_json(CompilerMetricsTestSourceJob, s, lambda
        x: x.recompute_average().peak_memory_usage.kilobytes, ylabel='Kilobytes',
                          title='Peak Memory Usage'),

      mkname('include_size', s): generate_json(IncludeSizeJob, s,
                        lambda x: x.line_count, ylabel='LOC',
                        title='Preprocessed LOC', ),
      mkname('symbol_count', s): generate_json(StdSymbolsJob, s,
                       lambda x: x.symbol_count, ylabel='# Symbols',
                       title='Visible Symbols'),
      mkname('binary_size', s): generate_json(BinarySizeJob, s, lambda x: x.bytes,
                      ylabel='bytes', title='Object Size')
    }
    all_data.update(data)
  output_path.write_text(json.dumps(all_data, indent=2, cls=plotly.utils.PlotlyJSONEncoder))
  return all_data



def produce_graphs():
  items = {
      usr_time_page: 'usr-time',
      total_time_page: 'time',
      memory_page: 'memory',
      includes_page: 'include',
      symbols_page: 'symbols'
  }
  with tqdm.tqdm(items.items(), position=1) as pbar:
    for fn, route in pbar:
      pbar.set_postfix_str(route)
      with tqdm.tqdm(STD_DIALECTS, position=0) as pbar2:
        for s in pbar2:
          pbar2.set_postfix_str(s.value)
          std_val = s.value.replace('c++', '')
          page = fn(std_val)
          p = Path(f'/tmp/pages/{route}')
          p.mkdir(exist_ok=True, parents=False)
          (p / f'{std_val}.html').write_text(page)




def produce_graphs():
  items = {
      usr_time_page: 'usr-time',
      total_time_page: 'time',
      memory_page: 'memory',
      includes_page: 'include',
      symbols_page: 'symbols'
  }
  with tqdm.tqdm(items.items(), position=1) as pbar:
    for fn, route in pbar:
      pbar.set_postfix_str(route)
      with tqdm.tqdm(STD_DIALECTS, position=0) as pbar2:
        for s in pbar2:
          pbar2.set_postfix_str(s.value)
          std_val = s.value.replace('c++', '')
          page = fn(std_val)
          p = Path(f'/tmp/pages/{route}')
          p.mkdir(exist_ok=True, parents=False)
          (p / f'{std_val}.html').write_text(page)

if __name__ == '__main__':
  prepopulate()
  generate_json_file('/tmp/data.json')
