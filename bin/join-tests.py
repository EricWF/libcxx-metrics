#!/usr/bin/env python3
from pathlib import Path
import os
import sys
import argparse

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--out", type=str)
  parser.add_argument('files', nargs='*')
  args = parser.parse_args()

  text =''
  for f in args.files:
    text += '\n' + Path(f).read_text() + '\n'
  Path(args.out).write_text(text)

if __name__  == '__main__':
  main()
