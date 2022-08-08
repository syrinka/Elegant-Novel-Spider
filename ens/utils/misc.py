import subprocess
from typing import List, Dict, Iterable

from ens.models import Catalog, Chapter


def call(args: Iterable[str], quiet=False) -> int:
    """调用外部命令"""
    return subprocess.call(
        args, 
        stdout=subprocess.DEVNULL if quiet else None
    )


def executable_exists(name: str) -> bool:
    """判断外部命令是否存在"""
    return call(['where', name], True) == 0


class CatalogBuilder(object):
    """
    c = Catalog()
    c.vol(...)
    c.chap(...)
    c.chap(...)
    """
    def __init__(self):
        self.catalog = list()


    def vol(self, name: str):
        self.catalog.append({'name': name, 'chaps': []})
        return self


    def chap(self, cid: str, title: str):
        self.catalog[-1]['chaps'].append(Chapter(cid, title))
        return self


    def build(self) -> Catalog:
        return Catalog(self.catalog)
