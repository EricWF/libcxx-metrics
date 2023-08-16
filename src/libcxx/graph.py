import sys
from pathlib import Path
from libcxx.config import LIBCXX_VERSIONS_ROOT

from libcxx.job import *
from libcxx.types import *
from libcxx.jobs import *
import tempfile
import json
import tqdm
import seaborn as sns
import pandas as pd
LIBCXX_HEADER_ROOT = Path(os.path.expanduser('~/llvm-project/build/libcxx/include/c++/v1/'))
HEADERS = [p for p in LIBCXX_HEADER_ROOT.rglob('*') if p.is_file()]

LV = LibcxxVersion
LIBCXX_VERSIONS = LibcxxVersion.between(LV.v6, LV.trunk)
STD_DIALECTS = Standard.between(Standard.Cpp14, Standard.Cpp23)
HEADERS = STLHeader.small_core_header_sample()



import itertools

def populate_job(job):
  if obj := DBDataPoint.get_or_none(key=job.key):
    return None
  return job.run()

def create_jobs(cls):
  jobs = []
  for item in itertools.product(HEADERS, STD_DIALECTS, LIBCXX_VERSIONS):
    jobs += [cls.create_job(header=item[0], standard=item[1], libcxx=item[2])]
  print('Have %d keys' % len(jobs))
  return jobs

def prepop(cls):
  import multiprocessing
  with multiprocessing.Pool() as pool:
    jobs = create_jobs(cls)
    for res  in tqdm.tqdm(pool.imap(populate_job, jobs), total=len(jobs)):
      if res is None:
        continue
      k, v = res
      cls.store_datapoint(k, v)


def prepop_single(cls):
  jobs = create_jobs(cls)
  for j in tqdm.tqdm(jobs):
    res = populate_job(j)
    if res is None:
      continue
    k, v = res
    cls.store_datapoint(k, v)

import matplotlib.pyplot as plt


def plot_data(cls, std, getter, label='Symbol', additional_id=None):
  versions = list(LIBCXX_VERSIONS)
  versions.sort()
  headers = list(HEADERS)

  plt.figure(figsize=(10, 5))


  plt.title(f'STL {label} in C++ {std.value}')
  plt.xlabel('Version')
  plt.ylabel(f'{label} Count')

  dp = lambda **kwargs: getter(cls.datapoint_kv(**kwargs))


  for h in tqdm.tqdm(headers, position=0):
    plt.plot([v.value for v in versions], list([dp(libcxx=v, standard=std, header=h) for v in versions]), marker='o', label=h.value)

  plt.grid(True)

  plt.legend()
  if additional_id is None:
    astr = ''
  else:
    astr = f'-{additional_id}-'
  plt.legend(bbox_to_anchor=(1.02, 1.1), loc='upper left', borderaxespad=0)
  plt.savefig(os.path.expanduser(f'~/libcxx-graphs/{cls.__name__}-{astr}c++{std.value}.png'))
  plt.clf()



if __name__ == '__main__':
  if True:
    prepop(StdSymbolsJob)
    for s in tqdm.tqdm(STD_DIALECTS, position=1):
      plot_data(StdSymbolsJob, s, lambda x: x.symbol_count, 'Symbol')
  if True:
    prepop(IncludeSizeJob)
    for s in tqdm.tqdm(STD_DIALECTS, position=1):
      plot_data(IncludeSizeJob, s, lambda x: x.line_count, 'LOC')

  if True:
    for s in STD_DIALECTS:
      plot_data(CompilerMetricsJob, s, lambda x: x.recompute_average().peak_memory_usage.kilobytes, 'Kilobytes', additional_id='peak-memory')
      plot_data(CompilerMetricsJob, s, lambda x: x.recompute_average().total_execution_time.microseconds, 'Microseconds', additional_id='total-time')
      plot_data(CompilerMetricsJob, s, lambda x: x.recompute_average().user_execution_time.microseconds, 'Microseconds', additional_id='usr-time')


