class ENSError(Exception):
    """
    异常基类
    当不知道该抛出什么异常时，就抛它

    @param msg: str - 回显信息
    """
    msg: str = None

    def __rich__(self):
        if self.msg is None:
            msg = self.args[0]
        else:
            msg = self.msg.format(*self.args)
        return f'[red]{self.__class__.__name__}[/] {msg}'


# Local
class LocalError(ENSError):
    pass


class LocalNotFound(LocalError):
    pass


class LocalAlreadyExists(LocalError):
    pass


class InvalidLocal(LocalError):
    pass


class ChapMissing(LocalError):
    pass



# Remote
class RemoteError(ENSError):
    pass


class RemoteNotFound(RemoteError):
    """@param name"""
    pass


# Fetch
class FetchError(RemoteError):
    """@param reason"""
    pass


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


class Abort(ENSError):
    """@param reason"""
    pass
