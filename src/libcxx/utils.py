import subprocess
import asyncio
import shlex

async def arun(cmd, check=True, shell=False):
  if shell:
    if isinstance(cmd, list):
      cmd = shlex.join(cmd)
    proc = await asyncio.create_subprocess_shell(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  else:
    proc = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  out, _ = await proc.communicate()
  out = out.decode('utf-8').strip()
  if check and proc.returncode != 0:
    raise RuntimeError("Command {cmd} failed with code {proc.returncode}\nstdout:\n{stdout}\n")
  return proc.returncode, out

def run(cmd, check=True, shell=False):
  proc = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  out, _ = proc.communicate()
  out = out.decode('utf-8').strip()
  if check and proc.returncode != 0:
    raise RuntimeError("Command {cmd} failed with code {proc.returncode}\nstdout:\n{stdout}\n")
  return proc.returncode, out
