import pkgutil
import importlib
from dataclasses import asdict
from typing import Dict, Type

from ens.console import log
from ens.models import Novel, Info, Info_, Catalog
from ens.exceptions import RemoteNotFound


_dependencies = {
    'fetch': ('get_info', 'get_catalog', 'get_content'),
    'info': ('get_info',)
}


class Remote(object):
    """远程源

    新的远程源应继承此类并重写若干函数

    Class methods:
        status: 获取该远程源支持的功能
    """
    def __init_subclass__(cls) -> None:
        """patch `get_info()`

        from `(self, str) -> Info_` to `(self, Novel) -> Info`
        """
        cls._get_info = cls.get_info
        def patch(self, novel) -> Info:
            info_ = self._get_info(novel.nid)
            return Info(novel, **asdict(info_))
        cls.get_info = patch


    @classmethod
    def _is_overrided(cls, funcname: str) -> bool:
        """判断函数是否被重写"""
        return funcname in cls.__dict__


    @classmethod
    def status(cls) -> Dict[str, bool]:
        """获取该远程源支持的功能"""
        status = {}
        for feat, deps in _dependencies.items():
            status[feat] = all(
                cls._is_overrided(dep) for dep in deps
            )
        return status


    def get_info(self, novel: Novel) -> Info:
        """
        Raises:
            FetchError
        """
        raise NotImplementedError


    def get_catalog(self, nid: str) -> Catalog:
        """
        Raises:
            FetchError
        """
        raise NotImplementedError


    def get_content(self, nid: str, cid: str) -> str:
        """
        Raises:
            FetchError
        """
        raise NotImplementedError


def get_remote_list() -> Dict[str, Type[Remote]]:
    from ens.remotes import __path__
    remotes = {}
    for ff, modname, ispkg in pkgutil.iter_modules(__path__):
        fullname = 'ens.remote.' + modname
        try:
            exports = ff.find_module(fullname).load_module(fullname).exports
        except ModuleNotFoundError as e:
            log('loading {} failed for lack of module {}'.format(fullname, e.name))
            continue

        if isinstance(exports, tuple):
            name, remote = exports
            remotes[name] = remote
            log('find remote {} named as {}'.format(remote, name))
        elif isinstance(exports, dict):
            for name, remote in exports.items():
                remotes[name] = remote
                log('find remote {} named as {}'.format(remote, name))

    return remotes


def get_remote(name) -> Remote:
    """获取一个 Remote 实例"""
    try:
        return get_remote_list()[name]()
    except ImportError:
        raise RemoteNotFound(name)
