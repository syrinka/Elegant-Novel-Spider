import os
import tempfile
import difflib

from ens.console import run
from ens.typing import *


def flatten(catalog: Catalog, index: dict) -> str:
    piece = []
    for vol in catalog:
        piece.append(f'# {vol["name"]}')
        for cid in vol['cids']:
            piece.append(f'. {index[cid]} ({cid})')
    
    return '\n'.join(piece)


def unflatten(s) -> Catalog:
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


def catalog_lose(old, new) -> bool:
    """
    检查目录是否发生了减量更新
    """
    diff = difflib.ndiff(flatten(old), flatten(new))
    for line in diff:
        if line.startswith('-'):
            return True
    return False


def merge(old, new, index) -> Catalog:
    old, new = flatten(old, index), flatten(new, index)
    path1 = 'old-index'
    path2 = 'new-index'

    with open(path1, 'w', encoding='utf-8') as f:
        f.write(old)

    with open(path2, 'w', encoding='utf-8') as f:
        f.write(new)

    ret = run('smerge/smerge.exe', 'mergetool', path1, path2)
    if ret == 0:
        with open(path1, encoding='utf-8') as f:
            final = f.read()

        os.remove(path1)
        os.remove(path2)

        return unflatten(final)

    else:
        # 发生错误
        os.remove(path1)
        os.remove(path2)


if __name__ == '__main__':
    c1 = [
        {
            'name': '格林在地下城',
            'cids': ['11', '22', '44']
        }
    ]

    c2 = [
        {
            'name': '格林在地下城',
            'cids': ['11', '22', '33']
        }
    ]

    index = {'11': 'ASSD', '22': 'QWED', '33': 'REST', '44': 'Boom!'}

    print(merge(c1, c2, index))
