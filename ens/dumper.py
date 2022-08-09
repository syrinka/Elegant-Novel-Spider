import pkgutil
import importlib
from warnings import warn
from typing import List, Dict, Callable

from ens.models import Info, Catalog
from ens.exceptions import DumperNotFound


class Dumper(object):
    def dump(self, info: Info, catalog: Catalog, get_chap: Callable[[str], str], path: str):
        raise NotImplementedError


def get_dumper(name) -> Dumper:
    """获取一个 Dumper 实例"""
    name = name.replace('_', '-')
    try:
        name = f'ens.dumpers.{name}'
        return importlib.import_module(name).export()
    except ImportError:
        raise DumperNotFound(name)


def get_dumper_list() -> List[str]:
    from ens.dumpers import __path__
    dumpers = []
    for ff, name, ispkg in pkgutil.iter_modules(__path__):
        dumpers.append(name.replace('_', '-'))
    return dumpers
