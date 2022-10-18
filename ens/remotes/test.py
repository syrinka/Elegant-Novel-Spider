import time

from ens.remote import Remote
from ens.models import Info, Catalog
from ens.utils.remote import CatalogBuilder
from ens.exceptions import FetchError


class Test(Remote):
    def get_info(self, nid) -> Info:
        return Info(
            'A Good Book {}'.format(nid),
            'Anonymous', intro='A Marvo book.'
        )


    def get_catalog(self, nid) -> Catalog:
        c = CatalogBuilder()
        c.vol('第一章')
        for i in range(100):
            c.chap(f'{i:0>3}', f'title-[{i}]')

        return c.build()


    def get_content(self, nid, cid: str) -> str:
        time.sleep(1)
        return 'YESYESYES' + cid


exports = ('test', Test)
