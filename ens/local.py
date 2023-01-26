import os
import sqlite3
import time
from os.path import join, exists
from shutil import rmtree
from contextlib import contextmanager

import ens.paths as paths
from ens.console import logger
from ens.models import *
from ens.exceptions import *


_sql_chap = '''
CREATE TABLE IF NOT EXISTS `data` (
    cid VARCHAR(128),
    content TEXT,
    PRIMARY KEY (cid)
);'''


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
        novel: Novel = None, *,
        path: str = None,
        new: Optional[bool] = False
    ):
        """
        Args:
            novel

        Raises:
            LocalNotFound: 指定本地缓存不存在
            InvalidLocal: 文件缺失或损坏
        """
        if path:
            pass
        elif novel:
            path = join(paths.LOCAL, novel.remote, novel.nid)
        else:
            raise ENSError()

        if not exists(path):
            raise LocalNotFound(path)
        self.path = path

        self.db_path = join(path, 'data.db')

        if new:
            self.write_file('info.yml', Info(novel).dump())
            self.write_file('catalog.yml', '')
            sqlite3.connect(self.db_path).cursor().execute(_sql_chap)

        try:
            _info = self.read_file('info.yml')
            self.info = Info.load(_info)
            _catalog = self.read_file('catalog.yml')
            self.catalog = Catalog.load(_catalog)
        except FileNotFoundError:
            raise InvalidLocal(path)


    def read_file(self, file) -> str:
        path = join(self.path, file)
        return open(path, 'r', encoding='utf-8').read()

    
    def write_file(self, file, text) -> int:
        path = join(self.path, file)
        return open(path, 'w', encoding='utf-8').write(text)

    
    @classmethod
    def from_path(cls, path):
        return cls(path=path)


    @classmethod
    def new(cls, novel: Novel):
        """创建一个本地缓存"""
        _path = join(paths.LOCAL, novel.remote)
        if not exists(_path):
            os.mkdir(_path)
        
        path = join(paths.LOCAL, novel.remote, novel.nid)
        if exists(path):
            raise LocalAlreadyExists(path)
        os.mkdir(path)

        return cls(novel, new=True)


    @classmethod
    def remove(cls, novel: Novel):
        """删除本地缓存"""
        path = join(paths.LOCAL, *novel)
        rmtree(path)


    @contextmanager
    def conn(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        yield conn, cursor
        cursor.close()
        conn.close()


    def has_chap(self, cid: str) -> bool:
        """
        Args:
            cid (str): chapter ID

        Returns:
            has (bool): True if has chapter
        """
        with self.conn() as (conn, cursor):
            cursor.execute('SELECT cid FROM `data` WHERE cid=?', (cid,))
            return cursor.fetchone() is not None


    def get_chap(self, cid: str) -> str:
        """
        Args:
            cid (str): chapter ID

        Returns:
            content (str): chapter content

        Raises:
            KeyError: 当缓存中没有对应章节的数据
        """
        with self.conn() as (conn, cursor):
            cursor.execute('SELECT content FROM `data` WHERE cid=?', (cid,))
            data = cursor.fetchone()

        if data is None:
            raise KeyError
        else:
            return data[0]


    def set_chap(self, cid: str, content: str):
        """
        Args:
            cid (str): chapter ID
            content (str): chapter content
        """
        with self.conn() as (conn, cursor):
            cursor.execute(
                'REPLACE INTO `data` VALUES (?, ?)',
                (cid, content) # 去掉多余的换行
            )
            conn.commit()


    def update_info(self, info: Optional[Info] = None):
        """更新小说的信息，并写入缓存
        
        Args:
            info (Info, optional)
        """
        if info is not None:
            self.info = info
        self.write_file('info.yml', self.info.dump())

    
    def update_catalog(self, catalog: Optional[Catalog] = None):
        """更新小说的目录
        
        Args:
            info (Catalog, optional)
        """
        if catalog is not None:
            self.catalog = catalog
        self.write_file('catalog.yml', self.catalog.dump())


    def isolate(self):
        """标记该小说为孤立小说"""
        self.info.isolated = True
        self.set_info()


    def prune(self):
        pass


def get_local_shelf(filter: Optional[Filter] = None) -> Shelf:
    if filter is None:
        filter = Filter(None)

    shelf = Shelf()

    time1 = time.time()
    for remote in os.listdir(paths.LOCAL):
        if not os.path.isdir(os.path.join(paths.LOCAL, remote)):
            continue
        if not filter.is_remote_in_scope(remote):
            continue

        for nid in os.listdir(join(paths.LOCAL, remote)):
            path = join(paths.LOCAL, remote, nid, 'info.yml')
            info = Info.load(open(path, encoding='utf-8').read())
            if not filter(info):
                continue
            shelf += info

    time2 = time.time()
    logger.debug('get local shelf in {:.4f}s'.format(time2 - time1))

    return shelf


def get_local_info(novel: Novel) -> Info:
    path = join(paths.LOCAL, novel.remote, novel.nid, 'info.yml')
    try:
        return Info.load(open(path, encoding='utf-8').read())
    except FileNotFoundError:
        raise LocalNotFound(novel)
