import os
import difflib
from tempfile import mkstemp

from ens.config import config
from ens.exceptions import ExternalError, FeatureUnsupport
from ens.models import Catalog
from ens.utils.exec import call, executable


def merge(old: str, new: str, ext='.txt') -> str:
    if not executable(config.DO_MERGE or ''):
        raise FeatureUnsupport('merge')

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
    ret = call(config.DO_MERGE.format(old=path1, new=path2))

    with open(path2, encoding='utf-8') as f:
        final = f.read()

    os.close(fd1)
    os.remove(path1)
    os.remove(path2)

    if ret == 0:
        return final
    else:
        raise ExternalError(ret)


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


def edit(text, ext='.txt') -> str:
    if not executable(config.DO_EDIT or ''):
        raise FeatureUnsupport('edit')

    fd, path = mkstemp(ext)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)

    os.close(fd)
    ret = call(config.DO_EDIT.format(file=path))

    with open(path, encoding='utf-8') as f:
        final = f.read()

    os.remove(path)

    if ret == 0:
        return final
    else:
        raise ExternalError(ret)


if __name__ == '__main__':
    from ens.utils.remote import CatalogBuilder

    c1 = CatalogBuilder().vol('格林在地下城') \
        .chap('1', 'aa').chap('2', 'bb').chap('3', 'cc').build()

    c2 = CatalogBuilder().vol('备注') \
        .chap('5', 'note') \
        .vol('格林在地下城') \
        .chap('1', 'aa').chap('2', 'bb').build()

    print(merge_catalog(c1, c2))
