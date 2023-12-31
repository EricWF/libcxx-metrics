from libcxx.types import *
from pydantic import BaseModel, Field, model_validator
import multiprocessing
from pathlib import Path
import os, re, sys, rich, tempfile, json,  asyncio, random
import libcxx.db as db
from libcxx.db import DBDataPoint, init_db
import itertools
import tqdm
import random
random.seed(random.getrandbits(128))

RERUN_REPEATABLE = '--rerun' in sys.argv

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

class JobOutput(BaseModel):
  hash_value : int

JOBS_REGISTRY = set()

class LibcxxJob(BaseModel):
  root_path : Optional[Path] = None
  key : Any
  libcxx: Optional[LibcxxInfo]

  class Meta:
    repeatable = False
    runs_per_repeat = 50

  def __init_subclass__(cls, **kwargs):
    super().__init_subclass__(**kwargs)
    db.registry.add(cls.key_type())
    db.registry.add(cls.output_type())
    db.registry.add(cls)
    global JOBS_REGISTRY
    JOBS_REGISTRY.add(cls)

  @staticmethod
  def all_job_types():
    global JOBS_REGISTRY
    return list([j for j in JOBS_REGISTRY])

  @staticmethod
  def all_jobs():
    jobs = []
    for jt in LibcxxJob.all_job_types():
      jobs += jt.jobs()

    random.shuffle(jobs)
    return jobs

  @classmethod
  def meta(cls):
    return cls.Meta

  @classmethod
  def job_inputs(cls):
    possible = {
          'standard': Standard.between(Standard.Cpp14, Standard.Cpp23),
          'libcxx': LibcxxVersion.after(LibcxxVersion.v6),
          'input': [ti for ti in TestInputs],
          'header': STLHeader.small_core_header_sample(),
          'debug': [DebugOpts.OFF, DebugOpts.ON],
          'optimize': [OptimizerOpts.O0, OptimizerOpts.O2]
        }
    kf = set(cls.key_type().key_fields())
    return {k: v for k,v in possible.items() if k in kf}

  @classmethod
  def jobs(cls):
    jlist = []
    for k in cross_product(**cls.job_inputs()):
      new_j = cls.create_job(**k)
      jlist += [new_j]
    if cls.meta().repeatable and RERUN_REPEATABLE:
      new_jobs = []
      for j in jlist:
        for i in range(0, cls.meta().runs_per_repeat):
          new_jobs += [j]
      random.shuffle(new_jobs)
      jlist = new_jobs
    return list(jlist)

  @classmethod
  def plotkey_inputs(cls):
    return {k: v for k,v in cls.job_inputs().items() if k not in ['libcxx', 'std', 'standard']}

  @classmethod
  def plotkeys(cls):
    return [PlotKey.create(**pk) for pk in cross_product(**cls.plotkey_inputs())]

  def hash_value(self):
    return hash(self.key)

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

  @contextlib.contextmanager
  def tmp_file_guard(self, name, contents=None):
    fa = tempfile.NamedTemporaryFile(prefix=str(Path(name).stem), suffix=str(Path(name).suffix),  dir=self.tmp_path, delete=False)
    tmp_file = Path(fa.name)
    fa.close()

    if contents is not None:
      tmp_file.write_text(contents)
    try:
      yield tmp_file
    finally:
      tmp_file.unlink(missing_ok=True)


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
    job =  cls.model_validate({'key': key, 'libcxx': key.libcxx.load()})
    return job

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

      obj, created = DBDataPoint.get_or_create(key=self.key, job=self.job_name(), defaults={'value': result})
      if not created:
        if self.meta().repeatable:
          obj.value.extend(result)
        else:
          obj.value = result
        obj.save()
      return obj

  def db_append(self, result):
      assert self.meta().repeatable
      obj, created = DBDataPoint.get_or_create(key=self.key, job=self.job_name(), defaults={'value': result})
      if not created:
        obj.value.extend(result)
        obj.save()
      return obj

  @classmethod
  def db_clear(cls):
      query = DBDataPoint.delete().where(DBDataPoint.job == cls.job_name())
      query.execute()

  def should_rerun(self, rerun_repeatable=RERUN_REPEATABLE):
    if rerun_repeatable and self.meta().repeatable:
      return True
    return not self.db_contains()

  def db_contains(self):
    return DBDataPoint.get_or_none(DBDataPoint.key == self.key) is not None

  def __call__(self, rerun_repeatable=RERUN_REPEATABLE, cache=True):
    if cache and (not self.meta().repeatable or not rerun_repeatable):
      if obj := self.db_get():
          return obj
    res = self.run()
    if res is None:
      raise RuntimeError('Result should not be none')
    if cache or self.meta().repeatable:
        self.db_store(res)
    return res



def named_product(**items):
    names = items.keys()
    vals = items.values()
    for res in itertools.product(*vals):
        yield dict(zip(names, res))

def cross_product(**job_inputs):
   return named_product(**job_inputs)



def run_return_job(job):
  try:
    res = job.run()
    return job, res
  except Exception as E:
    print(f'ERROR: \n{E}')
    raise E



def prepopulate_jobs_shuffeled(jobs):
  random.shuffle(jobs)

def prepopulate_jobs_by_running_threaded(jobs):
  jobs = list(jobs)
  print('Have %d jobs' % len(jobs))
  jobs = list([j for j in jobs if j.should_rerun()])
  prepopulate_jobs_shuffeled(jobs)
  if len(jobs) == 0:
    return
  with multiprocessing.Pool() as pool:
    for job,res in tqdm.tqdm(pool.imap(run_return_job, jobs, chunksize=64), total=len(list(jobs))):
      if res is None:
        pass
      job.db_store(res)

def prepopulate_jobs_by_running_singlethread(jobs):
  if len(jobs) == 0:
    return
  jobs = [j for j in jobs if j.should_rerun()]
  for job in jobs:
      res = job.run()
      if res is None:
        raise RuntimeError("IDK")
      job.db_store(res)


import asyncio
from asyncio import Queue, Semaphore


async def run_command_queue(done_event, queue, pbar):
    while not done_event.is_set():
          try:
            job = await queue.get()
            if job is None:
                return
            res = await job.arun()
            job.db_store(res)
          finally:
            pbar.update(1)
            queue.task_done()


async def async_run_jobs(jobs):
  print('Pruning the jobs')
  jobs = [j for j in jobs if j.should_rerun()]
  print('Shuffling the jobs')
  random.seed(random.getrandbits(256))
  random.shuffle(jobs)
  NUM_THREADS = 64
  with tqdm.tqdm(total=len(jobs)) as pbar:
    done_event = asyncio.Event()
    queue = asyncio.Queue()
    workers = [run_command_queue(done_event, queue, pbar) for _ in range(NUM_THREADS)]
    producer = [await queue.put(j) for j in jobs]


    print('Stopping the workers')


    print('Joining the queue')

    await queue.join()
    done_event.set()
    await asyncio.gather(*workers)
    print('done joining')
  pbar.close()

