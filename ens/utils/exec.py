import subprocess
from typing import List


def call(args: List[str], quiet=False) -> int:
    """调用外部命令"""
    return subprocess.call(
        args, 
        stdout=subprocess.DEVNULL if quiet else None
    )


def executable_exists(name: str) -> bool:
    """判断外部命令是否存在"""
    return call(['where', name], True) == 0
