import pkgutil
from typing import Dict, Type, TypedDict

from ens.console import logger
from ens.models import Catalog, Novel, RemoteInfo

_dependencies = {
    'fetch': ('get_info', 'get_catalog', 'get_content'),
    'info': ('get_info',),
}


class GetInfoKwargs(TypedDict):
    nid: str
    novel: Novel


class Remote(object):
    """远程源

    新的远程源应继承此类并重写若干函数

    Class methods:
        status: 获取该远程源支持的功能

    Raises:
        FileNotFoundError
            当预期的数据不存在，这可能是由于以下原因
            - 小说不存在
            - 小说被删除
            - 章节不存在
            - 章节被删除
            - 章节未审核通过
            若抛出该异常时，则不再重试
        Exception
            一般的运行时错误，例如：
            - 请求超时
            - 连接中断
            - 服务端拒绝响应
        Abort
            立即终止
    """
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


    def get_info(self, nid: str) -> RemoteInfo:
        """
        Raises:
            FileNotFoundError
            Exception
            Abort
        """
        raise NotImplementedError


    def get_catalog(self, nid: str) -> Catalog:
        """
        Raises:
            FileNotFoundError
            Exception
            Abort
        """
        raise NotImplementedError


    def get_content(self, nid: str, cid: str) -> str:
        """
        Raises:
            FileNotFoundError
            Exception
            Abort
        """
        raise NotImplementedError


def get_remote_list() -> Dict[str, Type[Remote]]:
    from ens.remotes import __path__
    remotes = {}
    for ff, modname, _ispkg in pkgutil.iter_modules(__path__):
        fullname = 'ens.remote.' + modname
        try:
            exports = ff.find_spec(fullname).loader.load_module(fullname).exports # type: ignore
        except ModuleNotFoundError as e:
            logger.warning('loading {} failed for lack of module {}'.format(fullname, e.name))
            continue

        if isinstance(exports, tuple):
            name, remote = exports
            remotes[name] = remote
            logger.debug('find remote {} named as {}'.format(remote, name))
        elif isinstance(exports, dict):
            for name, remote in exports.items():
                remotes[name] = remote
                logger.debug('find remote {} named as {}'.format(remote, name))

    return remotes


def get_remote(name) -> Remote:
    """获取一个 Remote 实例"""
    try:
        return get_remote_list()[name]()
    except ImportError as e:
        raise KeyError(f'未找到名为 {name} 的 remote') from e
