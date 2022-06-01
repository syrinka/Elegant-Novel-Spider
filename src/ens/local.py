import os
import sqlite3
import time
from os.path import join, exists
from shutil import rmtree
from collections import namedtuple
from contextlib import contextmanager

import ens.paths as paths
import ens.config as conf
from ens.utils import yaml_load, yaml_dump
from ens.console import log
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
    @raise LocalNotFound 如果本地库不存在
    @raise LocalAlreadyExists 如果通过 Local.init 尝试创建已存在的本地库
    @raise InvalidLocal
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

        try:
            _info = yaml_load(path=self.info_path)
            self.info = Info.load(_info)
        except FileNotFoundError:
            raise InvalidLocal(code)

    
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

        yaml_dump(Info(code).dump(), info_path)

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


    def catalog(self) -> Dict:
        return yaml_load(path=self.catalog_path)


    def spine(self) -> List[str]:
        """
        获取目录的脊，由所有 cid 组成
        """
        spine = []
        for vol in self.catalog():
            spine.extend(vol['cids'])
        return spine


    def nav(self):
        nav_node = namedtuple('nav', 'type title cid')
        index = self.get_index()
        nav = []
        for vol in self.catalog():
            nav.append(nav_node('vol', vol['name'], None))
            for cid in vol['cids']:
                nav.append(
                    nav_node('chap', index[cid], cid)
                )
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
            cursor.execute('SELECT cid FROM `chaps` WHERE cid=? AND content IS NOT NULL', (cid,))
            return cursor.fetchone() is not None


    def get_chap(self, cid: str) -> str:
        """
        @return chap_content
        @raise ChapMissing
        """
        with self.conn() as (conn, cursor):
            cursor.execute('SELECT content FROM `chaps` WHERE cid=?', (cid,))
            content = cursor.fetchone()[0]

        if content is None:
            raise ChapMissing(cid)
        else:
            return content


    def set_chap(self, cid: str, content: str) -> str:
        with self.conn() as (conn, cursor):
            cursor.execute(
                'UPDATE `chaps` SET content=? WHERE cid=?',
                (content.strip(), cid) # 去掉多余的换行
            )
            conn.commit()


    def get_title(self, cid: str) -> str:
        with self.conn() as (conn, cursor):
            cursor.execute('SELECT title FROM `chaps` WHERE cid=?', (cid,))
            return cursor.fetchone()[0]


    def get_index(self) -> Dict[str, str]:
        with self.conn() as (conn, cursor):
            cursor.execute('SELECT cid, title FROM `chaps`')
            return dict(cursor.fetchall())


    def vol_count(self) -> int:
        return len(self.catalog())


    def chap_count(self) -> int:
        return len(self.spine())


    def char_count(self) -> int:
        cnt = 0
        for cid in self.spine():
            cnt += len(self.get_chap(cid))
        return cnt


    def set_info(self, info: Info = None):
        """
        更新小说的信息
        """
        if info is not None:
            self.info.update(info)
        yaml_dump(self.info.dump(), self.info_path)

    
    def set_catalog(self, cat: Catalog):
        """
        更新小说的目录
        """
        yaml_dump(cat.catalog, self.catalog_path)

        with self.conn() as (conn, cursor):
            cursor.executemany(
                'INSERT OR IGNORE INTO `chaps` (cid, title) VALUES (?, ?)',
                cat.index.items()
            )
            conn.commit()


    def isolate(self):
        """
        标记该小说为孤立小说
        """
        self.info.isolated = True
        self.set_info()


    def prune(self):
        pass


def get_local_shelf(filter: Filter=None) -> Shelf:
    shelf = Shelf()

    time1 = time.time()
    for remote in os.listdir(paths.LOCAL):
        if filter:
            if not filter.remote_in_scope(remote):
                continue

        for nid in os.listdir(join(paths.LOCAL, remote)):
            path = join(paths.LOCAL, remote, nid, 'info.yml')
            info = Info.load(yaml_load(path=path))
            if filter:
                if not filter(info):
                    continue
            shelf += info
    time2 = time.time()
    log('get local shelf in {:.4f}s'.format(time2 - time1))

    return shelf


def get_local_info(code: Code) -> Info:
    path = join(paths.LOCAL, code.remote, code.nid, 'info.yml')
    try:
        _info = yaml_load(path=path)
    except FileNotFoundError:
        raise LocalNotFound(code)
        
    return Info.load(_info)
        

if __name__ == '__main__':
    c = Code('test~123')
    a = Local(c)
