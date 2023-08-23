import subprocess
import asyncio
import shlex

async def arun(cmd, check=True, shell=False, verbose=False):
  def vprint(*args):
    if verbose:
      print(*args)
  if shell:
    if isinstance(cmd, list):
      cmd = shlex.join(cmd)
    vprint(cmd)
    proc = await asyncio.create_subprocess_shell(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  else:
    if isinstance(cmd, str):
      cmd = shlex.split(cmd)
    vprint(cmd)
    proc = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  out, _ = await proc.communicate()
  out = out.decode('utf-8').strip()
  if check and proc.returncode != 0:
    raise RuntimeError("Command {cmd} failed with code {proc.returncode}\nstdout:\n{stdout}\n")
  return proc.returncode, out

def run(cmd, check=True, shell=False, verbose=False):
  if shell and isinstance(cmd, list):
    cmd = ' '.join(cmd)
  if verbose:
    print(cmd)
  proc = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  out, _ = proc.communicate()
  out = out.decode('utf-8').strip()
  if check and proc.returncode != 0:
    raise RuntimeError(f"Command {cmd} failed with code {proc.returncode}\nstdout:\n{out}\n")
  return proc.returncode, out
