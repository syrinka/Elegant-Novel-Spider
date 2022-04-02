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


class StatusError(ENSError):
    pass


class InvalidCode(ENSError):
    msg = 'Fail to parse code: {}.'


class BadCodeIndex(ENSError):
    msg = 'Expect code index to be in range 1~{}, receive {}'


class LocalError(ENSError):
    pass


class LocalNotFound(LocalError):
    pass


class LocalAlreadyExists(LocalError):
    pass


class ChapDataNotFound(LocalError):
    pass



class RemoteError(ENSError):
    pass


class RemoteNotFound(RemoteError):
    msg = 'Given remote {} not found.'


class DuplicateRemote(RemoteError):
    pass


class FetchError(RemoteError):
    pass



class DumpError(ENSError):
    pass


class DumperNotFound(DumpError):
    pass


class DuplicateDumper(DumpError):
    pass


class TopicNotFound(ENSError):
    pass



class MergeError(ENSError):
    pass
