import sys, os, re, subprocess, asyncio, rich, shutil, shlex
from pathlib import Path
from pydantic import BaseModel, RootModel, Field, model_validator, ConfigDict, constr
from libcxx.graph import GraphStore, GraphDefinition

import libcxx.db as db
from libcxx.utils import arun, run
import datetime
import peewee as pw
from typing import Optional, Union, Any
import tqdm
import pandas as pd
import plotly
import plotly.graph_objects as go
import plotly.express as px

@db.registry.add
class DiffStats(BaseModel):
  files : int = 0
  changed : int = 0
  added : int = 0
  deleted : int = 0
  changed_src_or_include : int = 0
  changed_test : int = 0

  def accumulate(self, olist):
    if not isinstance(olist, list):
      olist = [olist]
    for o in olist:
      for a in DiffStats.model_fields.keys():
        a1 = getattr(self, a)
        a2 = getattr(o, a)
        setattr(self, a, a1 + a2)
    return self

def graph_it(df):
  traces = []
  for h in df.columns[1:]:
    # Create a trace
    traces += [go.Scatter(
        x='date',
        y=df[h],
        mode='lines+markers',
        name=h
    )]

  return GraphDefinition.model_validate({
      "title": title,
      'x_label': x_label,
      "y_label": y_label,
      "data": traces  # This line includes the Plotly JSON in the output
  })
@db.registry.add
class GitCommitInfo(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  hash: str
  author_name : str
  author_email : str
  date: datetime.datetime
  title: str
  stats: DiffStats = Field(default_factory=DiffStats)


class CommitDB(db.LibcxxDBModel):
  hash = pw.TextField(primary_key=True, unique=True)
  author_name = pw.TextField()
  author_email = pw.TextField()
  date = pw.DateTimeField(default=datetime.datetime.now)
  title = pw.TextField()
  stats = db.PydanticModelType()

  def to_model_type(self):
    return GitCommitInfo.model_validate(self)

  @staticmethod
  def add_commit(info : GitCommitInfo):
    with db.DATABASE.atomic() as atx:
      obj, created = CommitDB.get_or_create(**{k: getattr(info, k) for k in info.model_fields.keys()})
      obj.save()

  @staticmethod
  def get_commit(hash):
    res = CommitDB.get_or_none(CommitDB.hash == hash)
    if res is None:
      return None
    return GitCommitInfo.model_validate(res)

    input_d = {}
    for k,v in GitCommitInfo.model_fields.items():
      annot = v.annotation
      input_d[k] = getattr()
  @staticmethod
  def contains_commit(hash):
    return CommitDB.get_commit(hash) is not None

  @staticmethod
  def get_commits_for_author(author):
    return CommitDB.select().where(CommitDB.author_name == author or CommitDB.author_email == author)







class GitBase(BaseModel):
  path: Path = Field(default_factory=lambda: Git.current_repository())
  git: Optional[Path] = Field(default_factory=lambda: Path(shutil.which('git')))


  @property
  def base_cmd(self):
    return list([str(self.git)] + ['-C', str(self.path)])


  @staticmethod
  def current_repository(path=None):
    cmd = ['git']
    cmd += [path] if path is not None else []
    cmd += ['rev-parse', '--show-toplevel']
    ret, output = run(cmd, check=False)
    if ret != 0:
      return None
    found_p = Path(output).absolute()
    assert found_p.is_dir()
    return found_p

  @staticmethod
  def _parse_git_commit_show(result):
    info_line = result[0]
    stat_lines = result[1:]

    commit_hash, author_name, author_email, commit_date, commit_title = info_line.split("<SPLIT>")
    commit = GitCommitInfo.model_validate({
                "hash": commit_hash,
                "author_name": author_name,
                "author_email": author_email,
                "date": datetime.datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%S%z"),
                "title": commit_title,
                'stats': GitBase.__post_process_git_commit_diff(stat_lines)
            })
    return commit

  @staticmethod
  def __post_process_git_commit_diff(result):
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

class Git(GitBase):
  def get_commit(self, hash, subpath=''):
    command = self.base_cmd + ['show', '--numstat', "--pretty=format:'%H<SPLIT>%an<SPLIT>%ae<SPLIT>%aI<SPLIT>%s'", f'{hash}']
    if subpath != '':
      command += ['--',  f"{subpath}"]

    exitcode, output = run(command)
    return GitBase._parse_git_commit_show(output.split('\n'))


  def commits_in_range(self, date1, date2, subpath=''):
    dstr1 = date1.isoformat()
    dstr2 = date2.isoformat()
    cmd = self.base_cmd + ['log',  '--pretty=format:"%H"',  f'--after={dstr1}', f'--before={dstr2}']
    if subpath:
      cmd += ['--', f'{self.path / subpath}']

    _, output = run(cmd, check=True, shell=True)
    parts = [l.strip() for l in  output.splitlines() if l.strip()]
    return parts


class AsyncGit(GitBase):
  async def get_commit(self, hash, subdir=''):
    command = self.base_cmd + ['show', '--numstat', "--pretty=format:'%H<SPLIT>%an<SPLIT>%ae<SPLIT>%aI<SPLIT>%s'", f'{hash}']
    if subdir:
      command += ['--',  f"{self.path / subdir}"]

    returncode, output = await arun(command, shell=True)
    return self._parse_git_commit_show(output.split('\n'))

  async def commits_in_range(self, date1, date2, subpath=''):
    if date1 > date2:
      tmp = date1
      date1 = date2
      date2 = tmp
    dstr1 = date1.isoformat()
    dstr2 = date2.isoformat()
    cmd = self.base_cmd + ['log',  '--pretty=format:"%H"',  f'--after={dstr1}', f'--before={dstr2}']
    if subpath:
      cmd += ['--', f'{subpath}']

    _, output = await arun(cmd, check=True, shell=True)
    parts = [l.strip() for l in  output.splitlines() if l.strip()]
    return parts

def main():
  db.init_db(db.DATABASE_TEST_PATH)
  start_date = datetime.datetime(year=2010, month=6, day=1)

  end_date = datetime.datetime.now()
  one_week = datetime.timedelta(days=365)
  now = datetime.datetime.now()
  num_weeks = (end_date - start_date).days / 365
  n = 0
  git = Git(path=os.path.expanduser("~/llvm-project"))
  while start_date + one_week <= now:
      next_date = start_date + one_week
      print(f'Starting year {n}')
      n += 1
      commit_range = git.commits_in_range(start_date, next_date, 'libcxx')
      print('Have %s commits' % len(commit_range))
      for l in commit_range:
        if not CommitDB.contains_commit(l):
          commit = git.get_commit(l)
          CommitDB.add_commit(commit)
          assert CommitDB.contains_commit(commit.hash)
        CommitDB.get_commit(l)
      start_date = next_date

def gather_data():
  db.init_db(db.DATABASE_TEST_PATH)
  frame = {'date': []}
  frame.update({k: [] for k in DiffStats.model_fields.keys()})

  last = None
  for data in CommitDB.select().where(CommitDB.date > datetime.datetime.now() - datetime.timedelta(days=2 * 365)).order_by(CommitDB.date).execute():
    data = data.to_model_type()
    if last is None:
      last = data.model_copy()
      continue
    if last.date.date() == data.date.date():
      last.stats.accumulate(data.stats)
      continue
    else:
      frame['date'] += [last.date]
      for k in DiffStats.model_fields.keys():
        frame[k] += [getattr(last.stats, k)]

      last = data
      continue
  frame['changed_r'] = pd.DataFrame(frame)['changed'].rolling(30, center=False).mean()
  df = pd.DataFrame(frame)
  print('Frame is %s len' % len(frame['date']))
  return df


def update_dates():
  db.init_db(db.DATABASE_TEST_PATH)
  for data in CommitDB.select():
    m = data.to_model_type()
    d = m.date.astimezone(datetime.timezone.utc)
    data.date = d
    data.save()

glist = GraphStore()
def do_it():
  df = gather_data()
  fig = go.Figure()
  gd =GraphDefinition.model_validate({'title': 'test', 'x_label': 'date', 'y_label': 'changed',
    'data': [go.Scatter(mode='lines', name='changed_r', x=df['date'], y=df['changed'])]})
  glist.root['test'] = gd
  Path('/tmp/data2.json').write_text(glist.dump_plotly_json())


  # Show the plot
  fig.show()

if __name__ == '__main__':
  do_it()

