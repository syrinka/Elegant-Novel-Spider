import time

from ens.remote import Remote
from ens.models import Catalog, Info
from ens.utils.remote import CatalogBuilder


class Test(Remote):
    def get_info(self, novel) -> Info:
        return Info(
            novel, 'A Good Book {}'.format(novel.nid),
            'Anonymous', intro='A Marvo book.'
        )


    def get_catalog(self, novel) -> Catalog:
        c = CatalogBuilder()
        c.vol('第一章')
        for i in range(10):
            c.chap(f'{i:0>3}', f'title-[{i}]')

        return c.build()


    def get_content(self, novel, cid: str) -> str:
        time.sleep(0.1)
        return 'YESYESYES' + cid


export = Test
