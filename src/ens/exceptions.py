class ENSError(Exception):
    msg = None
    def __init__(self, *args, **kw):
        if args or kw:
            if self.msg is None and len(args) == 1:
                self.msg = str(args[0])
            else:
                self.msg = self.msg.format(*args, **kw)
        else:
            self.msg = 'An Error Occur.'


    def __rich__(self):
        return f'[red]{self.__class__.__name__}[/] {self.msg}'


# Local
class LocalError(ENSError):
    pass


class LocalNotFound(LocalError):
    pass


class LocalAlreadyExists(LocalError):
    pass


class ChapMissing(LocalError):
    pass


# Remote
class RemoteError(ENSError):
    pass


class RemoteNotFound(RemoteError):
    msg = '远程源 {} 不存在'


class DuplicateRemote(RemoteError):
    pass


# Fetch
class FetchError(RemoteError):
    pass


class ChapError(FetchError):
    msg = '章节 {} 抓取失败, Reason: {}'


class ChapInvalid(FetchError):
    msg = '章节 {} 已失效'


class ChapUnauth(FetchError):
    msg = '章节 {} 无访问权限'


# Dumper
class DumpError(ENSError):
    pass


class DumperNotFound(DumpError):
    pass


class DuplicateDumper(DumpError):
    pass


# Misc
class StatusError(ENSError):
    pass


class InvalidCode(ENSError):
    msg = 'Fail to parse code: {}'


class BadCodeIndex(ENSError):
    msg = 'Expect code index to be in range 1~{}, receive {}'


class MergeError(ENSError):
    pass


class BadFilter(ENSError):
    pass


class TopicNotFound(ENSError):
    pass
