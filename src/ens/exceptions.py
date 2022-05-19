class ENSError(Exception):
    msg = None
    def __init__(self, *args, **kw):
        if len(args) == 1:
            self.msg = str(args[0])
        elif self.msg is None:
            self.msg = 'An Error Occur.'
        elif args or kw:
            self.msg = self.msg.format(*args, **kw)


    def __rich__(self):
        return f'[red]{self.__class__.__name__}[/] {self.msg}'


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


class Isolated(LocalError):
    """
    若在 fetch 过程中抛出了该异常，则标明正在抓取的小说已为孤立小说
    """
    msg = '该小说可能已被孤立 {}'



# Remote
class RemoteError(ENSError):
    pass


class RemoteNotFound(RemoteError):
    pass


# Fetch
class FetchError(RemoteError):
    pass


class ChapError(FetchError):
    msg = '章节 {} 抓取失败, Reason: {}'


# Dumper
class DumpError(ENSError):
    pass


class DumperNotFound(DumpError):
    pass


# Misc
class StatusError(ENSError):
    pass


class InvalidCode(ENSError):
    msg = 'Fail to parse code: {}'


class BadCodeIndex(ENSError):
    msg = 'Expect code index to be in range 1~{}, receive {}'


class MergeError(ENSError):
    msg = 'Merge fail, status code {}'


class BadFilter(ENSError):
    pass


class TopicNotFound(ENSError):
    pass


class Abort(ENSError):
    pass
