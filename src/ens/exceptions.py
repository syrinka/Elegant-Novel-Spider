from dataclasses import dataclass
from typing import Union, Tuple


class ENSError(Exception):
    msg = None

    def __rich__(self):
        if self.msg is None:
            msg = self.args
        else:
            msg = self.msg.format(** self.__dict__)
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
    pass


# Fetch
class FetchError(RemoteError):
    pass


class ChapError(FetchError):
    pass


# Dumper
class DumpError(ENSError):
    pass


class DumperNotFound(DumpError):
    pass


# Misc
class StatusError(ENSError):
    pass


@dataclass
class InvalidCode(ENSError):
    code_data: Union[str, Tuple]
    msg = 'Fail to parse code: {code_data}'


@dataclass
class BadCodeIndex(ENSError):
    index: int
    max_index: int
    msg = 'Expect code index to be in range 1~{max_index}, receive {index}'


@dataclass
class MergeError(ENSError):
    status: int
    msg = 'Merge fail, status code {status}'


class BadFilter(ENSError):
    pass


class TopicNotFound(ENSError):
    pass


class Abort(ENSError):
    pass
