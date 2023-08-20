#!/usr/bin/env python3
import subprocess
import sys
import os
import rich
from libcxx.graph import *

import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
assert PROJECT_ROOT.is_dir()


def upload_file(src, dst):
  CMD = ['gsutil', '-h', 'Cache-Control:"Cache-Control:private, max-age=0, no-transform"', 'cp', str(src), str(dst)]
  subprocess.run(CMD)
  print('Uploaded %s to %s' % (src, dst))

def main():
  init_db()
  parser = argparse.ArgumentParser()
  parser.add_argument('--data', type=str, required=False, default=None)
  args = parser.parse_args()
  if args.data is None:
    rich.print('No data file specified... regenerating the data. This may take a while')
    generate_json_file('/tmp/data.json')
    rich.print('Generating done...')
    args.data = '/tmp/data.json'
  data_path = args.data
  want_files = {
    PROJECT_ROOT / 'src/libcxx/templates/index.html': 'gs://dl.efcs.ca/graph/index.html',
    data_path: 'gs://dl.efcs.ca/graph/data.json'
  }
  for k, v in want_files.items():
    upload_file(k, v)

if __name__ == '__main__':
  main()

