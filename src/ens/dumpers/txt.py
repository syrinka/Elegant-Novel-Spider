import os
from ens.dumper import Dumper


class TXTDumper(Dumper):
    name = 'txt'
    ext = '.txt'

    def init(self, meta):
        self.path = meta.path
        self.file = open(meta.path, 'w', encoding='utf-8')
        self.file.write(meta.info.title + '\n')


    def feed(self, type, data):
        if type == 'vol':
            self.file.write('Vol. ' + data + '\n\n')
        elif type == 'chap':
            self.file.write('Chap. {}\n{}\n\n'.format(
                data[0],
                data[1].strip()
            ))


    def dump(self):
        self.file.close()


    def abort(self):
        self.file.close()
        os.remove(self.path)
