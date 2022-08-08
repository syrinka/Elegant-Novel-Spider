import pkgutil
import importlib
from warnings import warn
from typing import Type, Dict, List

from ens.models import Code, Info, Catalog
from ens.exceptions import RemoteNotFound


_dependencies = {
    'fetch': ('get_info', 'get_catalog', 'get_content'),
    'info': ('get_info',)
}


class Remote(object):
    """
    与远程源进行交互的逻辑类
    远程源需继承此类并重写若干函数
    """
    def __init__(self):
        self.__remote_init__()
        pass


    def __remote_init__(self):
        pass


    @classmethod
    def _is_overrided(cls, funcname: str) -> bool:
        """
        判断函数是否被重写
        """
        return funcname in cls.__dict__


    @classmethod
    def status(cls) -> Dict:
        """
        判断能否支持某个功能
        """
        status = {}
        for feat, deps in _dependencies.items():
            status[feat] = all(
                cls._is_overrided(dep) for dep in deps
            )
        return status


    def get_info(self, code: Code) -> Info:
        raise NotImplementedError


    def get_catalog(self, code: Code) -> Catalog:
        raise NotImplementedError


    def get_content(self, code: Code, cid: str) -> str:
        """
        @raise GetContentFail
        """
        raise NotImplementedError


def get_remote(name) -> Type[Remote]:
    """
    获取远程源对应的逻辑类
    """
    name = name.replace('_', '-')
    try:
        name = f'ens.remotes.{name}'
        return importlib.import_module(name).export
    except ImportError:
        raise RemoteNotFound(name)


def get_remote_list() -> List[str]:
    from ens.remotes import __path__
    remotes = []
    for ff, name, ispkg in pkgutil.iter_modules(__path__):
        remotes.append(name.replace('_', '-'))
    return remotes
