import os
import sqlite3
from os.path import join, exists
from shutil import rmtree
from collections import namedtuple

import yaml

import ens.paths as paths
import ens.config as conf
from ens.typing import *
from ens.exceptions import *


_sql_chap = '''
CREATE TABLE IF NOT EXISTS `chaps` (
    cid VARCHAR(128),
    title TEXT,
    content TEXT,
    PRIMARY KEY (cid)
);'''


class Local(object):
    """
    本地库
    """
    def __init__(self, code: Code, *, path=None):
        if path is not None:
            self.path = path
        else:
            path = join(paths.LOCAL, *code)
            if not exists(path):
                raise LocalNotFound(code)
            self.path = path
        
        self.info_path = join(path, 'info.yml')
        self.catalog_path = join(path, 'catalog.yml')
        self.db_path = join(path, 'data.db')

        _info = yaml.load(open(
            self.info_path, 'r', encoding='utf-8'
        ), Loader=yaml.SafeLoader)
        self.info = Info.load(_info)

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
            raise LocalAlreadyExists(code)
        os.mkdir(path)

        info_path = join(path, 'info.yml')
        catalog_path = join(path, 'catalog.yml')
        db_path = join(path, 'data.db')

        yaml.dump(
            Info(code).dump(),
            open(info_path, 'w')
        )
        # catalog 默认值为空列表
        open(catalog_path, 'w').write('[]')
        sqlite3.connect(db_path).cursor().execute(_sql_chap)

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


    def nav(self):
        nav_node = namedtuple('nav', 'type title cid')
        index = self.get_index()
        nav = []
        for vol in self.catalog:
            nav.append(nav_node('vol', vol['name'], None))
            for cid in vol['cids']:
                nav.append(
                    nav_node('chap', index[cid], cid)
                )
        return nav


    def has_chap(self, cid: str) -> bool:
        self.cursor.execute('SELECT cid FROM `chaps` WHERE cid=? AND content IS NOT NULL', (cid,))
        return self.cursor.fetchone() is not None


    def get_chap(self, cid: str) -> str:
        self.cursor.execute('SELECT content FROM `chaps` WHERE cid=?', (cid,))
        content = self.cursor.fetchone()[0]
        if content is None:
            raise ChapMissing(cid)
        else:
            return content


    def set_chap(self, cid: str, content: str) -> str:
        with self.conn:
            self.cursor.execute(
                'UPDATE `chaps` SET content=? WHERE cid=?',
                (content, cid)
            )
            self.conn.commit()


    def get_title(self, cid: str) -> str:
        self.cursor.execute('SELECT title FROM `chaps` WHERE cid=?', (cid,))
        return self.cursor.fetchone()[0]


    def get_index(self) -> Dict[str, str]:
        self.cursor.execute('SELECT cid, title FROM `chaps`')
        return dict(self.cursor.fetchall())


    def vol_count(self) -> int:
        return len(self.catalog)


    def chap_count(self) -> int:
        return len(self.spine())


    def char_count(self) -> int:
        cnt = 0
        for cid in self.spine():
            cnt += len(self.get_chap(cid))
        return cnt


    def set_info(self, info: Info):
        """
        更新小说的信息
        """
        self.info = info
        yaml.dump(
            info.dump(),
            open(self.info_path, 'w', encoding='utf-8'),
            allow_unicode = True
        )

    
    def set_catalog(self, cat: Catalog):
        """
        更新小说的目录
        """
        self.catalog = cat.catalog
        yaml.dump(
            cat.catalog,
            open(self.catalog_path, 'w', encoding='utf-8'),
            allow_unicode = True
        )

        with self.conn:
            self.cursor.executemany(
                'INSERT OR IGNORE INTO `chaps` (cid, title) VALUES (?, ?)',
                cat.get_index().items()
            )
            self.conn.commit()


    def prune(self):
        pass


def get_local_shelf(all=False) -> Shelf:
    shelf = Shelf()
    for remote in os.listdir(paths.LOCAL):
        for nid in os.listdir(join(paths.LOCAL, remote)):
            path = join(paths.LOCAL, remote, nid, 'info.yml')
            _info = yaml.load(open(
                path, 'r', encoding='utf-8'
            ), Loader=yaml.SafeLoader)
            info = Info.load(_info)
            if info.valid or all:
                shelf += info

    return shelf


def get_local_info(code: Code) -> Info:
    path = join(paths.LOCAL, code.remote, code.nid, 'info.yml')
    try:
        _info = yaml.load(open(
            path, 'r', encoding='utf-8'
        ), Loader=yaml.SafeLoader)
    except FileNotFoundError:
        raise LocalNotFound(code)
        
    return Info.load(_info)
        

if __name__ == '__main__':
    c = Code('test~123')
    a = Local(c)
