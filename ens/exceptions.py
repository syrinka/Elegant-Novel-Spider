from dataclasses import dataclass
from typing import Union, Tuple
from typing import NewType, Type


# dummy type
Code_ = NewType('Code', Type)


class ENSError(Exception):
    """
    异常基类
    当不知道该抛出什么异常时，就抛它

    @param msg: str - 回显信息
    """
    msg: str = None

    def __rich__(self):
        if self.msg is None:
            msg = ', '.join(self.args)
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
    remote: str


# Fetch
class FetchError(RemoteError):
    pass


class GetContentFail(FetchError):
    cid: str
    reason: str = None


# Dumper
class DumpError(ENSError):
    pass


class DumperNotFound(DumpError):
    pass


# Misc
class StatusError(ENSError):
    pass


class InvalidCode(ENSError):
    code_data: Union[str, Tuple]


@dataclass
class BadCodeIndex(ENSError):
    index: int
    max_index: int
    msg = 'Expect 1~[p]{max_index}[/], receive [p]{index}[/]'


@dataclass
class MergeError(ENSError):
    status: int
    msg = 'Merge fail, status code [p]{status}[/]'


@dataclass
class BadFilterRule(ENSError):
    expr: str
    msg = '非法的过滤规则 [p]{expr}[/], 修正后重试'


class TopicNotFound(ENSError):
    topic: str


class Abort(ENSError):
    reason: str = None
