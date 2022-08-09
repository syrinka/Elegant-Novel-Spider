import pkgutil
import importlib
from warnings import warn
from typing import Type, List, Literal

from ens.models import DumpMetadata, DumperInput
from ens.exceptions import DumperNotFound


class Dumper(object):
    ext = None


    def init(self, meta: DumpMetadata):
        pass


    def feed(self, type: Literal['vol', 'chap'], data):
        """
        vol: str
        chap: title, content
        """
        pass


    def dump(self):
        pass


    def abort(self):
        pass


class FullDumper(object):
    def __init__(self, data: DumperInput):
        pass


def get_dumper(name) -> Type[Dumper]:
    """
    获取远程源对应的逻辑类
    """
    name = name.replace('_', '-')
    try:
        name = f'ens.dumpers.{name}'
        return importlib.import_module(name).export
    except ImportError:
        raise DumperNotFound(name)


def get_dumper_list() -> List[str]:
    from ens.dumpers import __path__
    dumpers = []
    for ff, name, ispkg in pkgutil.iter_modules(__path__):
        dumpers.append(name.replace('_', '-'))
    return dumpers
