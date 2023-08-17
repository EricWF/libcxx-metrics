from libcxx.types import *
from pydantic import BaseModel, Field, model_validator
import multiprocessing
from pathlib import Path
import rich
import sys
import os
import tempfile
from dataclasses import dataclass
import json
from typing import Callable
from dataclasses import dataclass, field
from threading import RLock
from pydantic import ConfigDict
from libcxx.db import DBDataPoint, init_db, DATABASE
import tqdm
from itertools import product, starmap
from collections import namedtuple

def _new_tmp_path():
  import tempfile
  return Path(tempfile.mkdtemp(prefix='libcxx-versioned-job')).absolute()

@contextlib.contextmanager
def cd_guard(new_dir):
  old_dir = Path(os.curdir).absolute()
  try:
    os.chdir(new_dir)
    yield new_dir
  finally:
    os.chdir(old_dir)



def Default(x):
  import copy

  return Field(default_factory=lambda: copy.copy(x))

class PlotKey(BaseModel):
  name : str
  key_parts: dict[str, Any] = Field(default_factory=dict)

  @staticmethod
  def create(**kwargs):
    def as_key(obj):
      if hasattr(obj, 'pathkey'):
        return obj.pathkey()
      else:
        return obj
    return PlotKey.model_validate({'name': '/'.join([as_key(o) for k,o in kwargs.items()]), 'key_parts': dict(kwargs)})


class JobKey(BaseModel):
  @classmethod
  def job_name(cls):
    n = cls.__qualname__
    n = n.replace('__main__.', '')
    assert len(n.split('.')) == 2
    return n.split('.')[0]

  @classmethod
  def key_fields(cls):
    return (k for k in cls.model_fields)

  def key(self):
    parts = [self.job_name()]
    for f in self.key_fields():
      parts += [getattr(self, f)]
    return tuple(parts)


  def __hash__(self):
    return hash(self.key())

  def __eq__(self, other):
    if not isinstance(other, JobKey):
      return False
    return self.key() == other.key()

  def pathkey(self):
    def as_key(obj):
      if hasattr(obj, 'pathkey'):
        return obj.pathkey()
      else:
        return obj
    return '/'.join([as_key(o) for o in self.key()])



init_db()

class LibcxxJobResult(BaseModel):
  job: Any
  result: Any

class LibcxxJob(BaseModel):
  root_path : Optional[Path] = None

  key : Any
  libcxx: Optional[LibcxxInfo]

  @classmethod
  def job_inputs(cls):
    possible = {
          'standard': Standard.between(Standard.Cpp11, Standard.Cpp23),
          'libcxx': LibcxxVersion.after(LibcxxVersion.v6),
          'input': [TestInputs.vector, TestInputs.shared_ptr],
          'header': STLHeader.small_core_header_sample(),
          'debug': [DebugOpts.OFF, DebugOpts.ON],
          'optimize': [OptimizerOpts.O0, OptimizerOpts.O2]
        }
    kf = set(cls.key_type().key_fields())
    return {k: v for k,v in possible.items() if k in kf}

  @classmethod
  def jobs(cls):
    obj = cross_product(**cls.job_inputs())
    j = []
    for k in obj:
      j += [cls.create_job(**k)]
    return j

  @classmethod
  def plotkey_inputs(cls):
    return {k: v for k,v in cls.job_inputs().items() if k not in ['libcxx', 'std', 'standard']}

  @classmethod
  def plotkeys(cls):
    return [PlotKey.create(**pk) for pk in cross_product(**cls.plotkey_inputs())]



  @classmethod
  def from_key(cls, key):
    return cls.model_validate({
        'key': key,
        'libcxx': key.libcxx.load()
    })

  @model_validator(mode='after')
  def validate_paths(self):
    if self.root_path is None:
      self.root_path = Path(f'/tmp/libcxx-jobs', self.key.pathkey())
      self.root_path.mkdir(exist_ok=True, parents=True)
    if not self.root_path.is_dir():
        raise RuntimeError('No such directory: %s' % self.root_path)
    (self.root_path / 'tmp').mkdir(exist_ok=True)
    (self.root_path / 'out').mkdir(exist_ok=True)
    return self

  @model_validator(mode='after')
  def validate_libcxx(self):
    if self.libcxx is None:
      self.libcxx = self.key.libcxx.load()
    return self

  @property
  def tmp_path(self):
    return self.root_path / 'tmp'

  @property
  def output_path(self):
    return self.root_path / 'out'

  def output_dir(self, subdir):
    p = self.output_path / subdir
    p.mkdir(exist_ok=True, parents=True)
    return p

  def tmp_dir(self, subdir):
    p = self.tmp_path / subdir
    p.mkdir(exist_ok=True, parents=True)
    return p

  def output_file(self, subpath_file, contents=None):
    p = self.output_dir(Path(subpath_file).parent) / Path(subpath_file).name
    if contents is not None:
      p.write_text(contents)
    return p

  def tmp_file(self, subpath_file, contents=None):
    p = self.tmp_dir(Path(subpath_file).parent) / Path(subpath_file).name
    if contents is not None:
      p.write_text(contents)
    return p


  @classmethod
  def job_name(cls):
    n = cls.__qualname__
    n = n.replace('__main__.', '')
    return n

  @classmethod
  def key_type(cls):
    return cls.Key

  @classmethod
  def output_type(cls):
    return cls.Output


  @classmethod
  def create_key(cls, **kwargs):
    return cls.key_type().model_validate(kwargs)

  @classmethod
  def create_job(cls, **kwargs):
    key = cls.create_key(**kwargs)
    return cls.model_validate({'key': key, 'libcxx': key.libcxx.load()})

  def run_internal(self):
    raise NotImplementedError()

  def db_get(self, allow_missing=True):
    obj = DBDataPoint.get_or_none(key=self.key, job=self.job_name())
    if obj:
      if isinstance(obj, tuple):
        assert False
      return obj.value
    if not allow_missing:
      raise RuntimeError("Cache entry missing for %s" % self.key)
    return None

  def db_store(self, result):
    assert not isinstance(result, tuple)
    assert isinstance(result, self.output_type())
    obj, created = DBDataPoint.get_or_create(key=self.key, job=self.job_name(), value=result)
    if not created:
      obj.value = result
      obj.save()
    return obj

  @classmethod
  def db_clear(cls):
    with DATABASE.atomic():
      query = DBDataPoint.delete().where(DBDataPoint.job == cls.job_name())
      query.execute()

  def __call__(self,  cache=True):
    if cache:
      if obj := self.db_get():
        return obj
    res = self.run()
    if res is None:
      raise RuntimeError('Result should not be none')
    if cache:
      self.db_store(res)
    return res

def named_product(**items):
    names = items.keys()
    vals = items.values()
    for res in itertools.product(*vals):
        yield dict(zip(names, res))

def cross_product(**job_inputs):
   return named_product(**job_inputs)


def create_jobs(cls, *, job_inputs):
    jobs = [cls.create_job(**fields) for fields in cross_product(**job_inputs)]
    return jobs

def jobs_to_plotkeys(jobs):
  res = set()
  for j in jobs:
    res.add(j.key.plotkey())
  return res

def run_return_job(job):
  res = job.run()
  return job, res

def prepopulate_jobs_by_running_threaded(jobs):
  jobs = list(jobs)
  print('Have %d jobs' % len(jobs))
  jobs = list([j for j in jobs if j.db_get() is None])
  if len(jobs) == 0:
    return

  with multiprocessing.Pool() as pool:
    for job,res in tqdm.tqdm(pool.imap_unordered(run_return_job, jobs), total=len(list(jobs))):
      if res is None:
        raise RuntimeError("IDK")
      job.db_store(res)

def prepopulate_jobs_by_running_singlethread(jobs):
  if len(jobs) == 0:
    return
  jobs = [j for j in jobs if j.db_get() is None]
  for job in jobs:
      res = job.run()
      if res is None:
        raise RuntimeError("IDK")
      job.db_store(res)
