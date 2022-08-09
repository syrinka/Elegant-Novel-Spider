import subprocess
from typing import List, Union


def call(args: Union[str, List[str]], quiet=False) -> int:
    """调用外部命令"""
    pipe = subprocess.DEVNULL if quiet else None
    return subprocess.call(args, stdout=pipe, stderr=pipe)


def executable(cmd: str) -> bool:
    """判断外部命令是否存在"""
    app = cmd.split(maxsplit=1)[0]

    return call(['where', app], True) == 0
