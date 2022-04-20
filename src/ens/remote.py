import pkgutil

import ens.remotes as remotes
from ens.typing import *
from ens.exceptions import *


_dependencies = {
    'fetch': ('get_info', 'get_catalog', 'get_content'),
    'info': ('get_info',)
}


class Remote(object):
    """
    与远程源进行交互的逻辑类
    远程源需继承此类并重写若干函数
    """
    all_remotes = dict()

    def __init__(self, code: Code):
        self.code = code
        self.__remote_init__(code)
        pass


    def __init_subclass__(cls) -> None:
        name = cls.__module__.rsplit('.', 1)[-1]
        if name in cls.all_remotes:
            raise DuplicateRemote(name)
        cls.all_remotes[name] = cls


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


    def get_info(self) -> Info:
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
        return Remote.all_remotes[name]
    except KeyError:
        raise RemoteNotFound(name)


for ff, name, ispkg in pkgutil.iter_modules(remotes.__path__):
    name = 'ens.remotes.' + name
    ff.find_module(name).load_module(name)
