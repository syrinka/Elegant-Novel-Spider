import importlib
import pkgutil
from typing import Callable, List

from ens.models import Catalog, LocalInfo


class Dumper(object):
    def dump(self, info: LocalInfo, catalog: Catalog, get_chap: Callable[[str], str], path: str):
        raise NotImplementedError


def get_dumper(name) -> Dumper:
    """获取一个 Dumper 实例"""
    name = name.replace('_', '-')
    try:
        name = f'ens.dumpers.{name}'
        return importlib.import_module(name).export()
    except ImportError as e:
        raise KeyError(f'未找到名为 {name} 的 dumper') from e


def get_dumper_list() -> List[str]:
    from ens.dumpers import __path__
    dumpers = []
    for _ff, name, _ispkg in pkgutil.iter_modules(__path__):
        dumpers.append(name.replace('_', '-'))
    return dumpers
