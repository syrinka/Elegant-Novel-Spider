class ENSError(Exception):
    msg = 'An Error Occur'
    def __init__(self, *args, **kw):
        if args or kw:
            self.msg = self.msg.format(*args, **kw)


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



class RemoteError(ENSError):
    pass


class RemoteNotFound(RemoteError):
    msg = 'Given remote {} not found.'


class DuplicateRemote(RemoteError):
    pass


class FetchError(RemoteError):
    pass
