from dataclasses import dataclass, field
from typing import Any, Type
from threading import RLock

@dataclass
class ClassRegistry:
  mapping : dict[str, Type] = field(default_factory=dict)
  _lock : RLock = field(default_factory=RLock)

  class Tombstone:
    pass

  def add(self, obj_type):
    with self._lock:
      name = obj_type.__qualname__
      assert name not in self.mapping
      self.mapping[name] = obj_type
    return obj_type

  def get(self, key, default=Tombstone):
    with self._lock:
      if obj := self.mapping.get(key, None):
        return obj
    if default == ClassRegistry.Tombstone:
      raise KeyError("Key %s not present" % key)
    return default

  def __getitem__(self, key):
    return self.get(key)

  def __contains__(self, item):
    with self._lock:
      return item in self.mapping

  def items(self):
    return self.mapping.items()

registry = ClassRegistry()
