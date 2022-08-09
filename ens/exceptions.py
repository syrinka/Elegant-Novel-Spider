class ENSError(Exception):
    """
    异常基类
    当不知道该抛出什么异常时，就抛它

    @param msg: str - 回显信息
    """
    msg: str = None

    def __rich__(self):
        if self.msg is None:
            msg = ' '.join(self.args)
        else:
            msg = self.msg.format(*self.args)
        return f'[red]{self.__class__.__name__}[/] {msg}'


# Local
class LocalError(ENSError):
    pass


class LocalNotFound(LocalError):
    """@param path"""


class LocalAlreadyExists(LocalError):
    """@param path"""


class InvalidLocal(LocalError):
    """@param path"""


# Remote
class RemoteError(ENSError):
    pass


class RemoteNotFound(RemoteError):
    """@param name"""
    pass


class MaybeIsolated(RemoteError):
    msg = '该小说可能已在远端被删除'


# Fetch
class FetchError(RemoteError):
    """@param reason"""
    pass


class DataNotFound(FetchError):
    """当请求的数据不存在，这可能是由于以下原因
    
    - 小说不存在
    - 小说被删除
    - 章节不存在
    - 章节被删除
    - 章节未审核通过

    当抛出该异常时，将会跳过重试阶段

    @param reason
    """
    pass


class RequestError(FetchError):
    """当网络出现异常，这可能是由于以下原因

    - 连接超时
    - 服务器不可用

    @param reason
    """


# Dumper
class DumpError(ENSError):
    pass


class DumperNotFound(DumpError):
    """@param name"""
    pass


# Misc
class CacheError(ENSError):
    """@param msg"""
    pass


class InvalidNovel(ENSError):
    """@param bad_novel"""
    pass


class ExternalError(ENSError):
    """当调用外部程序失败时
    @param status
    """
    msg = 'return code {0}'


class BadFilterRule(ENSError):
    """@param rule"""
    msg = '非法的过滤规则 {0}'
