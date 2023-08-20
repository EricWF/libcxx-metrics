import subprocess
import os
from collections import defaultdict
import datetime
from pathlib import Path
import json
from libcxx.types import *
from libcxx.job import *
from libcxx.utils import *
import datetime
from pydantic import BaseModel, Field, model_validator
from typing import Optional, Any
import statistics
from libcxx.db import registry
from libcxx.config import LLVM_PROJECT_ROOT
LIBCXX_SRC_ROOT = LLVM_PROJECT_ROOT / 'libcxx'


class DiffStats(BaseModel):
  files : int = Field(default=0)
  changed : int = Field(default=0)
  added : int  = Field(default=0)
  deleted : int  = Field(default=0)
  changed_src_or_include : int  = Field(default=0)
  changed_test : int  = Field(default=0)

  @property
  def test_to_src_ratio(self):
    return (float(self.changed_test) / max(self.changed_src_or_include, 1))

class Accumulator(BaseModel):
  values: list[Union[int, float]] = Field(default_factory=list)

  @property
  def mean(self):
    return statistics.mean(self.values)

  @property
  def median(self):
      return statistics.median(self.values)

  @property
  def total(self):
    return sum(self.values)

  @property
  def stddev(self):
    return statistics.stddev(self.values)

  def __len__(self):
    return len(self.values)

class DiffStatsAccumulator(BaseModel):
  stats : list[DiffStats] = Field(default_factory=list)

  def append(self, st):
    self.stats += [st]

  def extend(self, st):
    self.stats.extend(st)

  @property
  def test_to_src_ratio(self):
    return Accumulator(values=[f.test_to_src_ratio for f in self.stats])

  @property
  def files(self):
    return Accumulator(values=[f.files for f in self.stats])

  @property
  def changed(self):
    return Accumulator(values=[f.changed for f in self.stats])

  @property
  def added(self):
    return Accumulator(values=[f.added for f in self.stats])

  @property
  def deleted(self):
    return Accumulator(values=[f.deleted for f in self.stats])

  @property
  def changed_test(self):
    return Accumulator(values=[f.changed_test for f in self.stats])

  @property
  def changed_src_or_include(self):
    return Accumulator(values=[f.changed_src_or_include for f in self.stats])



class GitCommitInfo(BaseModel):
  commit_hash: str
  author_name : str
  author_email : str
  commit_date: datetime.datetime
  commit_title: str
  stats: DiffStats = Field(default_factory=DiffStats)

async def agit_log_between_tags(tag1, tag2):
  command = f"git log --pretty=format:'%H<SPLIT>%an<SPLIT>%ae<SPLIT>%aI<SPLIT>%s' {tag1}..{tag2} -- {str(LIBCXX_SRC_ROOT)}"

  returncode, result = await arun(command, shell=True)
  result = result.split('\n')
  commits = []
  for line in tqdm.tqdm(result, position=1):
        if line:
            commit_hash, author_name, author_email, commit_date, commit_title = line.split("<SPLIT>")
            commits.append(GitCommitInfo.model_validate({
                "commit_hash": commit_hash,
                "author_name": author_name,
                "author_email": author_email,
                "commit_date": datetime.datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%S%z"),
                "commit_title": commit_title,
                'stats': await agit_commit_diff(commit_hash)
            }))
  return commits

def git_log_between_tags(tag1, tag2):
    command = f"git log --pretty=format:'%H<SPLIT>%an<SPLIT>%ae<SPLIT>%aI<SPLIT>%s' {tag1}..{tag2} -- {str(LIBCXX_SRC_ROOT)}"

    result = subprocess.check_output(command, shell=True).decode("utf-8").split("\n")
    commits = []
    for line in result:
        if line:
            commit_hash, author_name, author_email, commit_date, commit_title = line.split("<SPLIT>")
            commits.append(GitCommitInfo.model_validate({
                "commit_hash": commit_hash,
                "author_name": author_name,
                "author_email": author_email,
                "commit_date": datetime.datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%S%z"),
                "commit_title": commit_title,
                'stats': git_commit_diff(commit_hash)
            }))
    return commits

def git_commit_diff(commit_hash):
    command = f"git show --numstat --pretty='' {commit_hash} -- {str(LIBCXX_SRC_ROOT)}"
    result = subprocess.check_output(command, shell=True).decode("utf-8").split('\n')
    return post_process_git_commit_diff(result)

async def agit_commit_diff(commit_hash):
    command = f"git show --numstat --pretty='' {commit_hash} -- {str(LIBCXX_SRC_ROOT)}"
    returncode, result = await arun(command, shell=True)
    return post_process_git_commit_diff(result.split('\n'))


def post_process_git_commit_diff(result):
    loc_info = DiffStats()
    num_files = 0
    for line in result:
        if line:
            addition, deletion, filename = line.split("	")
            loc_info.files += 1
            if addition == '-' or deletion == '-':
              continue
            loc_info.changed += int(addition) + int(deletion)
            loc_info.added += int(addition)
            loc_info.deleted += int(deletion)

            if os.path.sep.join(["test", ""]) in filename:
                loc_info.changed_test += int(addition) + int(deletion)
            if os.path.sep.join(["src", ""]) in filename or os.path.sep.join(["include", ""]) in filename:
                loc_info.changed_src_or_include += int(addition) + int(deletion)
    return loc_info


@registry.registered
class LibcxxGitStatsJob(LibcxxJob):
  @registry.registered
  class Key(JobKey):
    libcxx: LibcxxVersion

  @registry.registered
  class Output(JobOutput):
    libcxx: LibcxxVersion
    commits: list[GitCommitInfo] = Field(default_factory=list)
    stats: DiffStatsAccumulator = Field(default_factory=DiffStatsAccumulator)

    def add_commit(self, ct):
      self.commits.append(ct)
      self.stats.append(ct.stats)

  def run(self):
    os.chdir(LLVM_PROJECT_ROOT)
    versions = [l for l in LibcxxVersion]
    before = versions[versions.index(self.key.libcxx)-1]

    b = before
    e = self.key.libcxx

    logs = git_log_between_tags(b.git_tag(), e.git_tag())
    ne = self.output_type().model_validate({
        'libcxx': b,
        'hash_value': hash(self.key),
    })
    for c in logs:
      ne.add_commit(c)
    return ne

  async def arun(self):
    os.chdir(LLVM_PROJECT_ROOT)
    versions = [l for l in LibcxxVersion]
    before = versions[versions.index(self.key.libcxx)-1]

    b = before
    e = self.key.libcxx

    logs = await agit_log_between_tags(b.git_tag(), e.git_tag())
    ne = self.output_type().model_validate({
        'libcxx': b,
        'hash_value': hash(self.key),
    })
    for c in logs:
      ne.add_commit(c)
    return ne


  @classmethod
  def job_inputs(cls):
    possible = {
          'libcxx': LibcxxVersion.after(LibcxxVersion.v7)
        }
    return possible

def ratio(x, y):
  import math
  div = math.gcd(x, y)
  return f"{x/div}:{y/div}"
  return str(int(round(x / (math.gcd(50, 10)),0))) + ':'+ str(int(round(y / (math.gcd(50, 10)),0)))


if __name__ == '__main__':
    init_db()
    jobs = LibcxxGitStatsJob.jobs()
    prepopulate_jobs_by_running_threaded(jobs)

    res = jobs[0].db_get()
    print(f'For version: {jobs[0].key}')
    rich.print(ratio(res.stats.changed_src_or_include.total, res.stats.changed_test.total))

    res = jobs[-1].db_get()
    print(f'For version: {jobs[-1].key}')
    rich.print(ratio(res.stats.changed_src_or_include.total, res.stats.changed_test.total))


    rich.print(res.stats.changed_src_or_include.mean)



