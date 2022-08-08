import os
import difflib
from tempfile import mkstemp
from typing import List

from ens.models import Catalog
from ens.exceptions import MergeError
from ens.utils.exec import call, executable_exists


def merge(old: str, new: str, ext='.txt') -> str:
    if old == new:
        return new

    fd1, path1 = mkstemp(ext)
    fd2, path2 = mkstemp(ext)

    with open(path1, 'w', encoding='utf-8') as f:
        f.write(old)

    with open(path2, 'w', encoding='utf-8') as f:
        f.write(new)

    # 解除对 path2 的占用，使 smerge 能写入文件
    os.close(fd2)
    ret = call(['smerge', 'mergetool', path1, path2, '-o', path2])

    with open(path2, encoding='utf-8') as f:
        final = f.read()

    os.close(fd1)
    os.remove(path1)
    os.remove(path2)

    if ret == 0:
        return final
    else:
        raise MergeError(f'Return novel: {ret}')


def catalog_lose(old: Catalog, new: Catalog) -> bool:
    """
    检查目录是否发生了减量更新
    """
    diff = difflib.ndiff(old.dump(), new.dump())
    for line in diff:
        if line.startswith('-'):
            return True
    return False


def merge_catalog(old: Catalog, new: Catalog) -> Catalog:
    return Catalog.load(
        merge(old.dump(), new.dump())
    )


if __name__ == '__main__':
    from ens.utils.exec import CatalogBuilder

    c1 = CatalogBuilder().vol('格林在地下城') \
        .chap('1', 'aa').chap('2', 'bb').chap('3', 'cc').build()

    c2 = CatalogBuilder().vol('备注') \
        .chap('5', 'note') \
        .vol('格林在地下城') \
        .chap('1', 'aa').chap('2', 'bb').build()

    print(merge_catalog(c1, c2))
