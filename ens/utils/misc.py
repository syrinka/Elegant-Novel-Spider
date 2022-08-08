import subprocess
from typing import List, Dict, Iterable

from ens.models import Catalog, Chapter


def flatten(catalog: List, index: Dict = None) -> str:
    piece = []
    for vol in catalog:
        piece.append(f'# {vol["name"]}')
        for cid in vol['cids']:
            if index is not None:
                piece.append(f'. {index.get(cid, "[新章节]")} ({cid})')
            else:
                piece.append(f'. {cid}')
    
    return '\n'.join(piece) + '\n'


def unflatten(s: str) -> List:
    catalog = []
    for i in s.split('\n'):
        if i.startswith('# '):
            catalog.append({
                'name': i[2:],
                'cids': []
            })
        elif i.startswith('. '):
            cid = i.rsplit('(', 1)[1][:-1]
            catalog[-1]['cids'].append(cid)
    return catalog


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
