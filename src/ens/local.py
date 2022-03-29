import os
import sqlite3
from os.path import join, dirname, exists
from shutil import rmtree

import yaml

import ens.paths as paths
import ens.config as conf
from ens.typing import *
from ens.exceptions import *


_sql_chap = '''
CREATE TABLE IF NOT EXISTS `chaps` (
    cid VARCHAR(128),
    content TEXT,
    PRIMARY KEY (cid)
);'''
_sql_index = '''
CREATE TABLE IF NOT EXISTS `index` (
    cid VARCHAR(128),
    title TEXT,
    PRIMARY KEY (cid)
);'''


class Local(object):
    """
    本地库
    Usage:
        local = Local(code)
        local = Local.from_path(path)
        try:
            local = Local(code)
        except LocalNotExists:
            local = Local.init(code)
    """
    INFO_KEYS = ('remote', 'nid', 'title', 'author', 'intro', 'last_update')

    def __init__(self, code: Code, *, path=None):
        if path is not None:
            self.path = path
        else:
            path = join(paths.LOCAL, *code)
            if not exists(path):
                raise LocalNotFound
            self.path = path
        
        self.info_path = join(path, 'info.yml')
        self.catalog_path = join(path, 'catalog.yml')
        self.db_path = join(path, 'data.db')

        _info = yaml.load(open(
            self.info_path, 'r', encoding='utf-8'
        ), Loader=yaml.SafeLoader)
        self.info = Novel(**_info)

        self.catalog = yaml.load(open(
            self.catalog_path, 'r', encoding='utf-8'
        ), Loader=yaml.SafeLoader)

        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    
    @classmethod
    def from_path(cls, path):
        return cls(path=path)

    
    @classmethod
    def init(cls, code: Code):
        """
        初始化一个本地库
        """
        p1 = join(paths.LOCAL, code.remote)
        if not exists(p1):
            os.mkdir(p1)
        
        path = join(p1, code.nid)
        if exists(path):
            raise LocalAlreadyExists
        os.mkdir(path)

        info_path = join(path, 'info.yml')
        catalog_path = join(path, 'catalog.yml')
        db_path = join(path, 'data.db')

        yaml.dump(
            dict.fromkeys(cls.INFO_KEYS),
            open(info_path, 'w')
        )
        open(catalog_path, 'w')
        sqlite3.connect(db_path).cursor() \
            .execute(_sql_chap) \
            .execute(_sql_index)

        return cls(code)


    @classmethod
    def remove(cls, code: Code):
        """
        删除本地库
        """
        path = join(paths.LOCAL, *code)
        rmtree(path)


    def spine(self) -> List[str]:
        """
        获取目录的脊，由所有 cid 组成
        """
        spine = []
        for vol in self.catalog:
            spine.extend(vol['cids'])
        return spine


    def has_chap(self, cid: str) -> bool:
        self.cursor.execute('SELECT cid FROM `chaps` WHERE cid=? LIMIT 1', (cid,))
        return bool(self.cursor.fetchone())


    def get_chap(self, cid: str) -> str:
        self.cursor.execute('SELECT content FROM `chaps` WHERE cid=?', (cid,))
        try:
            return self.cursor.fetchone()[0]
        except TypeError:
            # 'NoneType' object is not subscriptable
            return None


    def set_chap(self, cid: str, content: str) -> str:
        with self.conn:
            self.cursor.execute(
                'REPLACE INTO `chaps` (cid, content) VALUES (?, ?)',
                (cid, content)
            )
            self.conn.commit()


    def get_chap_title(self, cid: str) -> str:
        self.cursor.execute('SELECT title FROM `index` WHERE cid=?', (cid,))
        try:
            return self.cursor.fetchone()[0]
        except TypeError:
            # 'NoneType' object is not subscriptable
            return None


    def vol_count(self) -> int:
        return len(self.catalog)


    def chap_count(self) -> int:
        return len(self.spine())


    def char_count(self) -> int:
        cnt = 0
        for cid in self.spine():
            cnt += len(self.get_chap(cid))
        return cnt


    def set_info(self, info: Novel):
        """
        更新小说的信息
        """
        self.info = info
        yaml.dump(
            info.as_dict(),
            open(self.info_path, 'w', encoding='utf-8'),
            allow_unicode = True
        )

    
    def set_catalog(self, catalog: Catalog):
        """
        更新小说的目录
        """
        self.catalog = catalog
        yaml.dump(
            catalog,
            open(self.catalog_path, 'w', encoding='utf-8'),
            allow_unicode = True
        )


    def set_index(self, index: dict):
        """
        更新章节名索引
        """
        with self.conn:
            self.cursor.executemany(
                'INSERT OR IGNORE INTO `index` (cid, title) VALUES (?, ?)',
                index.items()
            )
            self.conn.commit()


    def prune(self):
        pass

    
    def __contains__(self, cid: str) -> bool:
        return self.has_chap(cid)


def get_local_shelf() -> List[Novel]:
    shelf = Shelf()
    for remote in os.listdir(paths.LOCAL):
        for nid in os.listdir(join(paths.LOCAL, remote)):
            path = join(paths.LOCAL, remote, nid, 'info.yml')
            _info = yaml.load(open(
                path, 'r', encoding='utf-8'
            ), Loader=yaml.SafeLoader)
            shelf += Novel(**_info)

    return shelf
        

if __name__ == '__main__':
    c = Code('test~book1')
    a = Local(c)
