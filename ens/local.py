import time
from pathlib import Path
from shutil import rmtree

from ens.console import logger
from ens.exceptions import *
from ens.models import *

LOCAL = Path() / 'local'


class LocalStorage(object):
    """本地小说数据

    Attributes:
        path (str): 存储路径
        info (Info): 小说信息
        catalog (Catalog): 小说目录

    Class methods:
        from_path: 从文件路径打开
        new: 创建一个空的数据库

    Static methods:
        remove: 删除本地数据
    """
    def __init__(self,
        novel: Optional[Novel] = None,
        *,
        path: Optional[Union[str, Path]] = None,
        new: bool = False,
    ):
        """
        Args:
            novel

        Raises:
            KeyError: 指定本地缓存不存在
            ValueError: 文件缺失或损坏
        """
        if path:
            path = Path(path)
        elif novel:
            path = LOCAL / novel.remote / novel.nid
        else:
            raise Exception('path 与 novel 至少应传入一项')

        if not path.exists():
            raise KeyError(path)
        self.path = path

        if new and novel:
            self.write_file('info.yml', LocalInfo(novel).dump())
            self.write_file('catalog.yml', '')
            (self.path / 'data').mkdir()

        try:
            self.info = LocalInfo.load(self.read_file('info.yml'))
            self.catalog = Catalog.load(self.read_file('catalog.yml'))
            assert (self.path / 'data').exists()
        except (FileNotFoundError, AssertionError) as e:
            raise ValueError('损坏的数据库') from e


    def read_file(self, file) -> str:
        return (self.path / file).read_text(encoding='utf-8')


    def write_file(self, file, text) -> int:
        return (self.path / file).write_text(text, encoding='utf-8')


    @classmethod
    def from_path(cls, path):
        return cls(path=path)


    @classmethod
    def new(cls, novel: Novel):
        """创建一个本地缓存"""
        path = LOCAL / novel.remote / novel.nid
        path.mkdir(parents=True)
        return cls(novel, new=True)


    @classmethod
    def remove(cls, novel: Novel):
        """删除本地缓存"""
        path = LOCAL / novel.remote / novel.nid
        rmtree(path)


    def has_chap(self, cid: str) -> bool:
        """
        Args:
            cid (str): chapter ID

        Returns:
            has (bool): True if has chapter
        """
        return (self.path / 'data' / cid).exists()


    def get_chap(self, cid: str) -> str:
        """
        Args:
            cid (str): chapter ID

        Returns:
            content (str): chapter content

        Raises:
            KeyError: 当缓存中没有对应章节的数据
        """
        try:
            return (self.path / 'data' / cid).read_text('utf-8')
        except FileNotFoundError as e:
            raise KeyError from e


    def set_chap(self, cid: str, content: str):
        """
        Args:
            cid (str): chapter ID
            content (str): chapter content
        """
        (self.path / 'data' / cid).write_text(content, 'utf-8')


    def all_chaps(self):
        for i in (self.path / 'data').iterdir():
            yield i.name


    def update_info(self, info: Optional[LocalInfo] = None):
        """更新小说的信息，并写入缓存

        Args:
            info (Info, optional)
        """
        if info is not None:
            self.info = info
        (self.path / 'info.yml').rename(self.path / 'info.yml.bak')
        self.write_file('info.yml', self.info.dump())


    def update_catalog(self, catalog: Optional[Catalog] = None):
        """更新小说的目录

        Args:
            info (Catalog, optional)
        """
        if catalog is not None:
            self.catalog = catalog
        (self.path / 'catalog.yml').rename(self.path / 'catalog.yml.bak')
        self.write_file('catalog.yml', self.catalog.dump())


    def isolate(self):
        """标记该小说为孤立小说"""
        self.info.isolated = True
        self.update_info()


    def prune(self):
        pass


def get_local_shelf(filter: Optional[Filter] = None) -> Shelf:
    if filter is None:
        filter = Filter(None)

    shelf = Shelf()

    time1 = time.time()
    for remote in LOCAL.iterdir():
        if not remote.is_dir():
            continue
        if not filter.is_remote_in_scope(remote.name):
            continue

        for path in remote.iterdir():
            info = LocalInfo.load((path / 'info.yml').read_text(encoding='utf-8'))
            if not filter(info):
                continue
            shelf += info

    time2 = time.time()
    logger.debug('get local shelf in {:.4f}s'.format(time2 - time1))

    return shelf


def get_local_info(novel: Novel) -> LocalInfo:
    path = (LOCAL / novel.remote / novel.nid / 'info.yml')
    try:
        return LocalInfo.load(path.read_text(encoding='utf-8'))
    except FileNotFoundError as e:
        raise KeyError(novel) from e
