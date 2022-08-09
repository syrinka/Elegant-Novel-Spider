import pkgutil
import importlib
from warnings import warn
from typing import Dict, List

from ens.models import Novel, Info, Catalog
from ens.exceptions import RemoteNotFound


_dependencies = {
    'fetch': ('get_info', 'get_catalog', 'get_content'),
    'info': ('get_info',)
}


class Remote(object):
    """
    与远程源进行交互的逻辑类
    远程源应继承此类并重写若干函数
    """
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


    def get_info(self, novel: Novel) -> Info:
        """
        @raise FetchError
        """
        raise NotImplementedError


    def get_catalog(self, novel: Novel) -> Catalog:
        """
        @raise FetchError
        """
        raise NotImplementedError


    def get_content(self, novel: Novel, cid: str) -> str:
        """
        @raise FetchError
        """
        raise NotImplementedError


def get_remote(name) -> Remote:
    """获取一个 Remote 实例"""
    name = name.replace('-', '_')
    try:
        name = f'ens.remotes.{name}'
        return importlib.import_module(name).export()
    except ImportError:
        raise RemoteNotFound(name)


def get_remote_list() -> List[str]:
    from ens.remotes import __path__
    remotes = []
    for ff, name, ispkg in pkgutil.iter_modules(__path__):
        remotes.append(name.replace('_', '-'))
    return remotes
