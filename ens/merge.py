import os
import difflib
from tempfile import mkstemp

from ens.console import run
from ens.exceptions import MergeError
from ens.typing import *


def merge(old, new, ext='.yml') -> str:
    fd1, path1 = mkstemp(ext)
    fd2, path2 = mkstemp(ext)

    with open(path1, 'w', encoding='utf-8') as f:
        f.write(old)

    with open(path2, 'w', encoding='utf-8') as f:
        f.write(new)

    # 解除对 path2 的占用，使 smerge 能写入文件
    os.close(fd2)
    ret = run('smerge/smerge.exe', 'mergetool', path1, path2, '-o', path2)

    with open(path2, encoding='utf-8') as f:
            final = f.read()

    os.close(fd1)
    os.remove(path1)
    os.remove(path2)

    if ret == 0:
        return final
    else:
        raise MergeError(f'Return code: {ret}')


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


def catalog_lose(old, new) -> bool:
    """
    检查目录是否发生了减量更新
    """
    diff = difflib.ndiff(flatten(old), flatten(new))
    for line in diff:
        if line.startswith('-'):
            return True
    return False


def merge_catalog(old, new, index) -> List:
    old, new = flatten(old, index), flatten(new, index)
    return unflatten(merge(old, new))


if __name__ == '__main__':
    index = {i: 'Chap'+i for i in '12345'}

    c1 = [
        {
            'name': '格林在地下城',
            'cids': ['1','2','3','4','5']
        }
    ]

    c2 = [
        {
            'name': '备注',
            'cids': ['5']
        },
        {
            'name': '格林在地下城',
            'cids': ['1', '2', '3', '4', '6']
        }
    ]

    print(merge_catalog(c1, c2, index))
