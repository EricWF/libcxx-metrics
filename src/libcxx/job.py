from elib.libcxx.types import *
from pydantic import BaseModel, Field, model_validator

from pathlib import Path
import rich
import sys
import os
import tempfile
from dataclasses import dataclass
import json
from elib.ethread import syncronized
from typing import Callable
from  dataclasses import dataclass, field
from threading import RLock
from pydantic import ConfigDict
from elib.libcxx.db import DBDataPoint, init_db

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
    return '/'.join(self.key())

init_db()

class LibcxxJob(BaseModel):
  root_path : Optional[Path] = None

  key : Any
  libcxx: Optional[LibcxxInfo]

  @classmethod
  def from_key(cls, key):
    return cls.model_validate({
        'key': key,
        'libcxx': key.libcxx.load()
    })

  @model_validator(mode='after')
  def validate_paths(self):
    if self.root_path is None:
      self.root_path = Path(f'/tmp/libcxx-jobs', *self.key.key())
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


  @classmethod
  def datapoint(cls, key):
    obj = DBDataPoint.get_or_none(key=key, job=cls.job_name())
    if obj:
      if isinstance(obj, tuple):
        assert False
      return obj.value

    runner = cls.model_validate({'key': key, 'libcxx': key.libcxx.load()})
    res = runner.run()
    if res  is None:
      raise RuntimeError('Result should not be none')
    assert isinstance
    if isinstance(res, tuple):
      k, v = res
      res = v
    new_created = DBDataPoint.create(key=key, job=cls.job_name(), value=res)
    return res

  @classmethod
  def store_datapoint(cls, k, v):
    obj, created = DBDataPoint.get_or_create(job=cls.job_name(), key=k, value=v)

  @classmethod
  def datapoint_kv(cls, **kwargs):
    key = cls.key_type().model_validate(kwargs)
    return cls.datapoint(key)
