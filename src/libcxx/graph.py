import importlib

import plotly
import plotly.graph_objs as go
import pandas as pd
import tqdm
from libcxx.job import *
from libcxx.jobs import *
from jinja2 import Environment, FileSystemLoader

LIBCXX_VERSIONS = LibcxxVersion.between(LibcxxVersion.v7, LibcxxVersion.trunk)
STD_DIALECTS = Standard.between(Standard.Cpp14, Standard.Cpp23)
HEADERS = STLHeader.small_core_header_sample()

TEMPLATE_DIR = Path(__file__).absolute().parent / 'templates'
file_loader = FileSystemLoader(TEMPLATE_DIR)
jinja_env = Environment(loader=file_loader)

def prepopulate():
  mp_jobs = create_jobs(StdSymbolsJob, versions=LIBCXX_VERSIONS,
                        standards=STD_DIALECTS, headers=HEADERS)
  mp_jobs += create_jobs(IncludeSizeJob, versions=LIBCXX_VERSIONS,
                         standards=STD_DIALECTS, headers=HEADERS)
  prepopulate_jobs_by_running_threaded(mp_jobs)
  st_jobs = create_jobs(CompilerMetricsJob, versions=LIBCXX_VERSIONS,
                        standards=STD_DIALECTS, headers=HEADERS)
  prepopulate_jobs_by_running_threaded(st_jobs)

  #prepopulate_jobs_by_running_singlethread(st_jobs)

def generate_graph(cls, std, getter, ylabel, title):
  versions = list(LIBCXX_VERSIONS)
  versions.sort()
  headers = list(HEADERS)

  data = {
      'version': [v.value for v in versions]
  }
  dp = lambda **kwargs: getter(cls.create_job(**kwargs).db_get(allow_missing=False))

  for h in headers:
    data[h.value] = list(
        [dp(libcxx=v, standard=std, header=h) for v in versions])

  # Convert data to DataFrame
  df = pd.DataFrame(data)
  traces = []
  for h in headers:
    # Create a trace
    traces += [go.Scatter(
        x=df['version'],
        y=df[h.value],
        mode='lines+markers',
        name=h.value
    )]

  graphJSON = json.dumps(traces, cls=plotly.utils.PlotlyJSONEncoder)
  template = jinja_env.get_template('index.html')
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
  produce_graphs()
  prepopulate()
