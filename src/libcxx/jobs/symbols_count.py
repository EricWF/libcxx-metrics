import asyncio

from libcxx.job import *
from libcxx.types import *
import subprocess
import re
import shutil
from libcxx.db import registry
from types import SimpleNamespace

QUERY_STR = \
  '''
  set traversal IgnoreUnlessSpelledInSource
  set bind-root false
  m namedDecl(anyOf(cxxRecordDecl(isInStdNamespace()), functionDecl(isInStdNamespace())))
  '''.strip() + '\n'

class StdSymbolsJob(LibcxxJob):

  class Key(JobKey):
    libcxx: LibcxxVersion
    standard: Standard
    header: STLHeader

  class Output(BaseModel):
    symbol_count: int

  state : Any = Field(exclude=True, default=SimpleNamespace)

  def setup_state(self):
    self.state.input_file = self.tmp_file('input.cpp',
                               '#include <%s>\nint main() {\n}\n' % self.key.header.value)


    self.state.db_file = self.tmp_file('compile_commands.json',
                            CompilationDatabaseEntry.model_validate({
                                'directory': self.tmp_path,
                                'file': self.state.input_file,
                                'arguments': [shutil.which('clang++'),  self.key.standard.flag(), '-c'] + self.libcxx.include_flags() + ['-xc++', str(input_file)]
                            }).as_database().model_dump_json(indent=2))


    self.state.query_cmd = [shutil.which('clang-query'),
                 '-f', self.tmp_file('matcher.txt', QUERY_STR),
                 '-p', self.state.db_file] + [self.state.input_file]


  def postprocess_output(self, output):
    out = output.decode('utf-8').strip()
    last_line_re = re.compile('(?P<COUNT>\d+) matches.')
    m = last_line_re.match(out.splitlines()[-1])
    return StdSymbolsJob.Output.model_validate({
      'symbol_count': int(m.group('COUNT'))
    })

  def run(self):
    self.setup_state()
    out = subprocess.check_output(self.state.query_cmd)
    return self.postprocess_output(out)

  async def arun(self):
    self.setup_state()
    process = await asyncio.create_subprocess_exec(*self.state.query_cmd,
      stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
    stdout, _ = await process.communicate()
    if process.returncode != 0:
      raise RuntimeError('Process %s failed with %s \nstdout:\n%s\n' % (self.cmd, process.returncode,
      stdout.decode('utf-8')))
    return self.postprocess_output(stdout)

