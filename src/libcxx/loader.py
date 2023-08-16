from pydantic import BaseModel, Field
import importlib.util
import importlib.machinery
import inspect as inspect_module
import sys
import rich

class ModuleSpec(BaseModel):
  name : str = Field()
  path : str = Field()

  def load(self):
    if self.name in sys.modules:
      return importlib.reload(sys.modules[self.name])

    loader = importlib.machinery.SourceFileLoader(self.name, self.path)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    my_module = importlib.util.module_from_spec(spec)
    loader.exec_module(my_module)
    return my_module

  @staticmethod
  def create(obj):
    if isinstance(obj, tuple):
      raise RuntimeError('Cannot be this')
    name = inspect_module.getmodule(obj).__name__
    spec = importlib.util.find_spec(name)
    return ModuleSpec.model_validate({'name': spec.name, 'path': spec.origin})

class ClassLoaderSpec(ModuleSpec):
  class_name : str = Field()

  def load(self):
    mod = ModuleSpec.load(self)
    parts = self.class_name.split('.')
    obj = mod
    for p in parts:
      obj = getattr(obj, p)
    return obj

  @staticmethod
  def create(obj):
    base = ModuleSpec.create(obj)
    return ClassLoaderSpec.model_validate({
        **base.model_dump(),
        'class_name': obj.__class__.__qualname__,
    })

