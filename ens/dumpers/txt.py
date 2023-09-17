import os
from typing import Callable

from ens.dumper import Dumper
from ens.models import Catalog, LocalInfo


class TXTDumper(Dumper):
    ext = '.txt'

    def dump(self, info: LocalInfo, catalog: Catalog, get_chap: Callable[[str], str], path: str):
        file = open(path, 'w', encoding='utf-8')
        file.write(info.title + '\n')

        for nav in catalog.nav_list():
            if nav.type == 'chap':
                assert nav.index is not None
                cid = catalog.spine[nav.index].cid
                file.write('✦Chapter {}\n{}\n\n'.format( # Chapter
                    nav.title,
                    get_chap(cid),
                ))
            elif nav.type == 'vol':
                file.write('✧Volume ' + nav.title + '\n\n') # Volume

        file.close()


export = TXTDumper
