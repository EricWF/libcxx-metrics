import sys

from elib.ai.conversation import Conversation
from elib.ai.functions import *
from elib.ai.types import *
from libcxx.config import LIBCXX_INPUTS_ROOT
import rich
import sys
import os
from pathlib import Path
import json
from pydantic import BaseModel, RootModel, Field
from typing import Optional

class TestEntry(BaseModel):
  key: str
  overload: str
  done: Optional[bool] = Field(default=False)



class TestEntryList(RootModel):
  root : list[TestEntry] = Field(default_factory=list)

LIST_PATH = Path(__file__).parent.parent / "list.json"

def load_list():
  return TestEntryList.model_validate_json(LIST_PATH.read_text()).root

def save_list(l):
  ent = TestEntryList.model_validate(l)
  LIST_PATH.write_text(ent.model_dump_json(indent=2))

INCLUDE_FILE = LIBCXX_INPUTS_ROOT / 'include' / 'test_types_decl.h'
INCLUDE_TEXT = INCLUDE_FILE.read_text()

@ai_callable
class WriteTest(CallableBaseModel):
  """Save a C++ test to the specified output file"""
  output_file: str = Field(description="Save the file to this location")
  contents: str = Field(description="The test contents")

  def call(self):
    Path(self.output_file).write_text(self.contents)
    return f'Wrote test to {self.output_file}'

PROMPT = f'''
You are a C++ engineer who specializes is the STL and test writing. The user
will ask you to write a test for a specific overload of std::vector. Please
write a single test which minimally exercises the overload. 
Here are some rules:

  * Minimally exercise the overload. Don't add comments or commentary.
  
  * Output only the test function.
  
  * Use the provided test types if needed.
  
  * Do not output any preamble. The user will handle it.

```c++
{INCLUDE_TEXT}
```
'''
def run_once(ent : TestEntry):
  c = Conversation().echo_on().system(PROMPT).user(f'Please write a test for `{ent.overload}` in a function called `{ent.key}. '
  f'Save the test to /tmp/tests/{ent.key}.cpp`')\
   .add_function(WriteTest).streaming_chat(function_call='WriteTest')

jobs = load_list()
for obj in jobs:
  retries = 3
  while True:
    try:
      if not obj.done:
        run_once(obj)
      obj.done = True
      save_list(jobs)
      break
    except Exception as E:
      rich.print('')
      --retries
      if retries <= 0:
        raise E


