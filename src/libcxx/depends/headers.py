#!/usr/bin/env python3
import re
import os
import sys
from pathlib import Path
import rich
import re
from dataclasses import dataclass, field
import tempfile
from elib.libcxx.types import LibcxxInfo
import subprocess
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
from multiprocessing import Pool, JoinableQueue
import tqdm
LIBCXX_HEADER_ROOT = Path(os.path.expanduser('~/llvm-project/build/libcxx/include/c++/v1/'))
HEADERS = [p for p in LIBCXX_HEADER_ROOT.rglob('*') if p.is_file()]


include_re = re.compile(r'\s*\#\s*include\s*[<"]\s*(\S*)\s*[>"]\s*')

@dataclass
class HeaderDependencyExtractor:
  libcxx_info: LibcxxInfo
  bad_files: list[Path] = field(default_factory=list)
  compiler: str = 'clang++'
  compiler_flags: list[str] = field(default_factory=lambda: ['-std=c++20'])

  def _check_input_arg(self, file):
      file = Path(file)
      if not file.is_absolute() and not file.exists():
        for i in self.libcxx_info.include_paths:
          if (self.path, i, file).is_file():
            file = i / file
            break

      file = Path(file).absolute()
      if not file.exists():
        raise RuntimeError('Could not find file: %s' % file)
      return file

  def _process_clang_deps(self, file, data):
    data = data.strip()
    if not data:
      return []

    src, dests = data.split(":")
    src = src.strip()
    if src != '-.o'  and Path(src).with_suffix('').name != Path(file).with_suffix('').name:
      raise RuntimeError('Dependency output structure not as expected')
    dests = [d.strip() for d in dests.split() if d.strip() and d.strip() != '\\']
    if len(dests) > 0:
      assert Path(file).absolute() == Path(dests[0]).absolute()
      dests = dests[1:]
    return dests

  def extract_using_compiler(self, file):
      file = Path(file)
      command =[self.compiler] + self.compiler_flags + self.libcxx_info.include_flags() + ['-M', '-xc++', '-']
      input = f'#include <{file}>\n'
      process = subprocess.run(' '.join(command), input=input, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
      if process.returncode != 0:
        print('Adding bad file: %s' % file)
        self.bad_files.append(file)

      deps = self._process_clang_deps(file, process.stdout)
      dependencies = []
      for d in deps:
        assert d and not d.endswith('\\')
        dependencies.append(Path(d).absolute())
      return dependencies



  def extract_using_regex(self, arg):
     file = Path(arg).absolute()
     text = file.read_text()
     lines = [include_re.match(i.strip()) for i in text.splitlines() if i.strip()]
     lines = [i.group(1) for i in lines if i is not None]
     return list(set([self.libcxx_info.absolute_header_path(i) for i in lines]))


@dataclass
class HeaderGraphBuilder:
  extractor : HeaderDependencyExtractor
  graph : dict = field(default_factory=lambda: defaultdict(list))
  verbose: bool = False
  extract_method : str = 'compiler'

  def _note(self, msg):
    if self.verbose:
      print(msg)

  def _unpathify(self, adj_list):
    new_list = defaultdict(list)
    for k,v in adj_list.items():
      new_list[str(k)] = list(set([str(vv) for vv in v]))
    return new_list

  def _do_compile(self, n):
    results = [r for r in self.extractor.extract_using_regex(n)]
    return (n, list(results),)



  def build_adj_list(self, initial_nodes, add_new_nodes=False, ignore_edge=lambda s, e: False, local_names=True):
    info = self.extractor.libcxx_info

    seen = set()
    to_see = list(initial_nodes)

    adj_list = {}

    while len(to_see) > 0:
      this_round = list(to_see)
      for i in this_round:
        seen.add(i)
      to_see = []
      with tqdm.tqdm(total=len(this_round)) as pbar:
          with Pool() as pool:
            for res in pool.imap_unordered(self._do_compile, this_round):
              pbar.update(1)
              src, edges = res
              edges = [e for e in edges if not ignore_edge(src, e)]
              for h in edges:
                if h not in seen and add_new_nodes:
                  to_see.append(h)
                  seen.add(h)
              assert src not in adj_list.keys()

              adj_list[src] = list(set([e for e in edges if (e in seen or add_new_nodes)] ))
      pool.close()
      pool.join()
    if local_names:
      result = defaultdict(list)
      for k,v in adj_list.items():
          result[info.relative_header_path(k)] = [info.relative_header_path(vv) for vv in v]
      adj_list = result
    return self._unpathify(adj_list)

  def add_header(self, file, extract_method = None):
    libcxx_info = self.extractor.libcxx_info
    if extract_method is None:
      extract_method = self.extractor.extract_using_clang
    deps = self.extractor.extract_using_compiler(file)
    key = info.relative_header_path(deps)

  def convert_to_top_level_adj_list(self, adj_list):
    info = self.extractor.libcxx_info
    def top_level_name(x):
      abs = info.absolute_header_path(x)
      if not info.is_libcxx_path(abs):
        return None
      rel = info.relative_header_path(abs)
      assert not rel.is_absolute()
      rp = rel.parts[0]
      assert len(rel.parts) < 5
      return rp
    new_adj = defaultdict(set)
    for k,v in tqdm.tqdm(adj_list.items()):
      tl = top_level_name(k)
      if tl is None:
        continue
      values = set([top_level_name(l) for l in v if top_level_name(l) is not None])
      new_adj[tl] |= values
    d = defaultdict(list)
    for k,v in new_adj.items():
      d[k] = list(v)
    return self._unpathify(d)

  def extract_nodes(self, adj_list, node_list):
    def is_allowed(x):
      return x in node_list or Path(x) in node_list or self.extractor.libcxx_info.absolute_header_path(x) in node_list

    new_adj = defaultdict(list)
    for k,v in adj_list.items():
      if not is_allowed(k):
        continue
      new_adj[k] = [vv for vv in v if is_allowed(vv)]



def plot_adj_list(adj_list):
  G = nx.Graph(adj_list)
  nx.draw(G, with_labels=True)
  plt.show()



"""

FILE_MAP = {}
keys = {'%s' % f: '%s' % f.relative_to(ROOT) for f in FILES}
not_found = []
import tqdm
for f in tqdm.tqdm(FILES):
    key = keys['%s' % f]
    print('Processing %s' % key)
    includes = extract_cpp_includes(f, key)
    for i in includes:
        if i not in keys.values():
            print('Key not in values: %s' % i)
            not_found += [i]
    FILE_MAP[key] = includes

if True:
    for n in not_found:
        FILE_MAP[n] = []




def is_cyclic_util(node, visited, rec_stack, Graph, visited_list):

    # Mark the current node as visited and
    # add it to recursion stack
    visited[node] = True
    rec_stack[node] = True
    visited_list.append(node)

    # iterate over all neighbouring nodes,
    # recur for those who are not visited yet
    for neighbour in Graph[node]:
        if visited[neighbour] == False:
            if is_cyclic_util(neighbour, visited, rec_stack, Graph, visited_list) == True:
                return True
        elif rec_stack[neighbour] == True:
            print('rec stack: %s' % neighbour)
            return True

    # remove the node from recursion stack
    rec_stack[node] = False
    visited_list.pop()
    return False

def is_cyclic(Graph):
    visited_list = []
    visited = {node: False for node in Graph}
    rec_stack = {node: False for node in Graph}
    for node in Graph:
        if visited[node] == False:
            if is_cyclic_util(node,visited,rec_stack, Graph, visited_list) == True:
                print(node)
                print(visited_list)
                return True
    return False

assert not is_cyclic(FILE_MAP)
"""
