import pkgutil

import ens.remotes as remotes
from ens.typing import *
from ens.exceptions import *


_dependencies = {
    'fetch': ('get_info', 'get_catalog', 'get_content')
}


class Remote(object):
    """
    与远程源进行交互的逻辑类
    远程源需继承此类并重写若干函数
    """
    _remotes = dict()
    name = None

    def __init__(self, code: Code):
        self.code = code
        self.__remote_init__(code)
        pass


    def __init_subclass__(cls) -> None:
        cls.name = cls.name or cls.__name__.lower()
        if cls.name in cls._remotes:
            raise DuplicateRemote(cls.name)
        cls._remotes[cls.name] = cls


    def __remote_init__(self, code: Code):
        pass


    @classmethod
    def _is_overrided(cls, funcname: str) -> bool:
        """
        判断函数是否被重写
        """
        return funcname in cls.__dict__


    @classmethod
    def status(cls) -> dict:
        """
        判断能否支持某个功能
        """
        status = {}
        for feat, deps in _dependencies.items():
            status[feat] = all(
                cls._is_overrided(dep) for dep in deps
            )
        return status


    def get_info(self) -> Novel:
        raise NotImplementedError


    def get_catalog(self) -> Catalog:
        raise NotImplementedError


    def get_content(self, cid: str) -> str:
        raise NotImplementedError


def get_remote(name) -> Type[Remote]:
    """
    获取远程源对应的逻辑类
    """
    try:
        return Remote._remotes[name]
    except KeyError:
        raise RemoteNotFound(name)


all_remotes = {}
for ff, name, ispkg in pkgutil.iter_modules(remotes.__path__):
    if name not in remotes.disabled:
        all_remotes[name] = True
        name = 'ens.remotes.' + name
        ff.find_module(name).load_module(name)
    else:
        all_remotes[name] = False
