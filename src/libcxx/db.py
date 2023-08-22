from pydantic import BaseModel, Field
from libcxx.types import *
import peewee as pw
from pathlib import Path
import sys
import os
import pydantic
from dataclasses import dataclass, field
from typing import Any
from threading import RLock
DATABASE = pw.SqliteDatabase(None)
DATABASE_PATH = Path(os.path.expanduser('~/.database/libcxx-info.db'))
DATABASE_TEST_PATH = Path(os.path.expanduser('~/.database/test/libcxx-info.db'))
import rich
from libcxx.registry import ClassRegistry

registry = ClassRegistry()
class PydanticWrapper(pydantic.BaseModel):
  registry_key : str
  raw_object : str

  def object(self):
    class_type = registry[self.registry_key]
    return class_type.model_validate_json(self.raw_object)

  @staticmethod
  def create(obj):
    assert obj.__class__.__qualname__ in registry
    return PydanticWrapper.model_validate({
        'registry_key': obj.__class__.__qualname__,
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
  key = PydanticModelType()
  value = PydanticModelType()
  job = pw.TextField()

  class Meta:
    database = DATABASE
    primary_key = pw.CompositeKey('key', 'job')


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
