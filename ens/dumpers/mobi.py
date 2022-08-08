import os

from ens.console import echo, doing, run
from ens.dumper import Dumper
from ens.dumpers.epub import EPUBDumper


class MOBIDumper(Dumper):
    ext = '.mobi'

    def init(self, meta) -> None:
        self.path = meta.path
        self.tmp_path = self.path + '.epub'
        meta.path = self.tmp_path

        self.epub = EPUBDumper()
        self.epub.init(meta)

    
    def feed(self, type, data):
        self.epub.feed(type, data)


    def dump(self):
        self.epub.dump()
        run('kindlegen.exe', self.tmp_path, '-o', os.path.basename(self.path))
        os.remove(self.tmp_path)


    def abort(self):
        self.epub.abort()
        os.remove(self.tmp_path)
