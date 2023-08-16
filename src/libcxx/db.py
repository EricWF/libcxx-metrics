from pydantic import BaseModel, Field
from libcxx.types import *
import peewee as pw
from pathlib import Path
import sys
import os
from libcxx.loader import *
import pydantic
from dataclasses import dataclass
from typing import Any
from threading import RLock
DATABASE = pw.SqliteDatabase(None)
DATABASE_PATH = Path(os.path.expanduser('~/.database/libcxx-info.db'))
DATABASE_TEST_PATH = Path(os.path.expanduser('~/.database/test/libcxx-info.db'))

@dataclass
class ClassRegistry:
  mapping : dict[str, Any]
  _lock : RLock()

  def registered(self, obj_type):
    with self._lock:
      name = obj_type.__name__
      assert name not in self.mapping
      self.mapping[name] = obj_type
    return obj_type

  def __getitem__(self, key):
    with self._lock:
      if obj := self.mapping.get(key, None):
        return obj
      raise KeyError("Key %s not present" % key)


class PydanticWrapper(pydantic.BaseModel):

  class_type : ClassLoaderSpec
  raw_object : str

  def object(self):
    class_type = self.class_type.load()
    return class_type.model_validate_json(self.raw_object)

  @staticmethod
  def create(obj):
    return PydanticWrapper.model_validate({
        'class_type': ClassLoaderSpec.create(obj),
        'raw_object': obj.model_dump_json(round_trip=True)
    })


class PydanticModelType(pw.TextField):
  field_type = 'base_model'

  def db_value(self, value):
    obj = PydanticWrapper.create(value)
    return obj.model_dump_json(round_trip=True)

  def python_value(self, value):
    obj = PydanticWrapper.model_validate_json(value)
    return obj.object()


class DBDataPoint(pw.Model):
  key = PydanticModelType(primary_key=True)
  value  = PydanticModelType()
  job = pw.TextField()

  class Meta:
    database = DATABASE


def init_db(path=DATABASE_PATH):
  if not DATABASE.is_closed():
    return
  DATABASE.init(path)
  if DATABASE.is_closed():
    DATABASE.connect()
    DATABASE.create_tables([DBDataPoint])



if __name__ == '__main__':
  init_db(path=DATABASE_PATH)
  import rich
  for item in DBDataPoint.select(DBDataPoint):
    rich.print(item)
    rich.print(item.value)
