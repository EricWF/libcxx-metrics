from libcxx.job import *
from libcxx.types import *
import subprocess
import re
import shutil
from libcxx.db import registry

QUERY_STR = \
  '''
  set traversal IgnoreUnlessSpelledInSource
  set bind-root false
  m namedDecl(anyOf(cxxRecordDecl(isInStdNamespace()), functionDecl(isInStdNamespace())))
  '''.strip() + '\n'

class StdSymbolsJob(LibcxxJob):
  @registry.registered
  class Key(JobKey):
    libcxx: LibcxxVersion
    standard: Standard
    header: STLHeader

  @registry.registered
  class Output(BaseModel):
    symbol_count: int

  def run(self):
    input_file = self.tmp_file('input.cpp',
                               '#include <%s>\nint main() {\n}\n' % self.key.header.value)


    db_file = self.tmp_file('compile_commands.json',
                            CompilationDatabaseEntry.model_validate({
                                'directory': self.tmp_path,
                                'file': input_file,
                                'arguments': [shutil.which('clang++'),  self.key.standard.flag(), '-c'] + self.libcxx.include_flags() + ['-xc++', str(input_file)]
                            }).as_database().model_dump_json(indent=2))


    query_cmd = [shutil.which('clang-query'),
                 '-f', self.tmp_file('matcher.txt', QUERY_STR),
                 '-p', db_file] + [input_file]

    out = subprocess.check_output(query_cmd).decode('utf-8').strip()
    last_line_re = re.compile('(?P<COUNT>\d+) matches.')
    m = last_line_re.match(out.splitlines()[-1])
    return StdSymbolsJob.Output(symbol_count=int(m.group('COUNT')))

