import os
from typing import Callable
from ens.dumper import Dumper
from ens.models import Info, Catalog


class TXTDumper(Dumper):
    ext = '.txt'

    def dump(self, info: Info, catalog: Catalog, get_chap: Callable[[str], str], path: str):
        file = open(path, 'w', encoding='utf-8')
        file.write(info.title + '\n')

        for nav in catalog.nav_list():
            if nav.type == 'chap':
                cid = catalog.spine[nav.index].cid
                file.write('◇Chapter {}\n{}\n\n'.format(
                    nav.title,
                    get_chap(cid)
                ))
            elif nav.type == 'vol':
                file.write('◆Volume ' + nav.title + '\n\n')

        file.close()


export = TXTDumper
