import os
import sqlite3
import time
from os.path import join, exists
from shutil import rmtree
from contextlib import contextmanager

import ens.paths as paths
from ens.console import log
from ens.models import *
from ens.exceptions import *


_sql_chap = '''
CREATE TABLE IF NOT EXISTS `data` (
    cid VARCHAR(128),
    content TEXT,
    PRIMARY KEY (cid)
);'''


class LocalStorage(object):
    """
    本地库
    @raise LocalNotFound 如果本地库不存在
    @raise LocalAlreadyExists 如果通过 Local.init 尝试创建已存在的本地库
    @raise InvalidLocal
    """
    def __init__(self, novel: Novel=None, path: str=None, init_flag: bool=False):
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

        if init_flag:
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
    def init(cls, novel: Novel):
        """初始化一个本地库"""
        _path = join(paths.LOCAL, novel.remote)
        if not exists(_path):
            os.mkdir(_path)
        
        path = join(paths.LOCAL, novel.remote, novel.nid)
        if exists(path):
            raise LocalAlreadyExists(path)
        os.mkdir(path)

        return cls(novel, init_flag=True)


    @classmethod
    def remove(cls, novel: Novel):
        """删除本地库"""
        path = join(paths.LOCAL, *novel)
        rmtree(path)


    def nav_list(self) -> List[NavPoint]:
        """用于供网页生成有层次的目录"""
        nav = []
        index = 0
        for vol in self.catalog.catalog:
            nav.append(NavPoint('vol', vol.title, None))
            for chap in vol.chaps:
                nav.append(NavPoint('chap', chap.title, index))
                index += 1
        return nav


    @contextmanager
    def conn(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        yield conn, cursor
        cursor.close()
        conn.close()


    def has_chap(self, cid: str) -> bool:
        with self.conn() as (conn, cursor):
            cursor.execute('SELECT cid FROM `data` WHERE cid=?', (cid,))
            return cursor.fetchone() is not None


    def get_chap(self, cid: str) -> str:
        """获取章节文本
        @return chap_content
        @raise KeyError 当本地存储中没有对应章节的数据
        """
        with self.conn() as (conn, cursor):
            cursor.execute('SELECT content FROM `data` WHERE cid=?', (cid,))
            content = cursor.fetchone()[0]

        if content is None:
            raise KeyError
        else:
            return content


    def set_chap(self, cid: str, content: str) -> str:
        with self.conn() as (conn, cursor):
            cursor.execute(
                'REPLACE INTO `data` VALUES (?, ?)',
                (cid, content.strip()) # 去掉多余的换行
            )
            conn.commit()


    def update_info(self, info: Info = None):
        """更新小说的信息"""
        if info is not None:
            self.info = info
        self.write_file('info.yml', self.info.dump())

    
    def update_catalog(self, catalog: Catalog = None):
        """更新小说的目录"""
        if catalog is not None:
            self.catalog = catalog
        self.write_file('catalog.yml', self.catalog.dump())


    def isolate(self):
        """标记该小说为孤立小说"""
        self.info.isolated = True
        self.set_info()


    def prune(self):
        pass


def get_local_shelf(filter: Filter=Filter(None)) -> Shelf:
    shelf = Shelf()

    time1 = time.time()
    for remote in os.listdir(paths.LOCAL):
        if not filter.is_remote_in_scope(remote):
            continue

        for nid in os.listdir(join(paths.LOCAL, remote)):
            path = join(paths.LOCAL, remote, nid, 'info.yml')
            info = Info.load(open(path, encoding='utf-8').read())
            if not filter(info):
                continue
            shelf += info
    time2 = time.time()
    log('get local shelf in {:.4f}s'.format(time2 - time1))

    return shelf


def get_local_info(novel: Novel) -> Info:
    path = join(paths.LOCAL, novel.remote, novel.nid, 'info.yml')
    try:
        return Info.load(open(path, encoding='utf-8').read())
    except FileNotFoundError:
        raise LocalNotFound(novel)
