import time

from ens.remote import Remote
from ens.typing import Catalog, Novel


class Test(Remote):
    def get_info(self) -> Novel:
        return Novel(
            self.code, 'A Good Book {}'.format(self.code.nid),
            'Anonymous', intro='A Marvo book.'
        )


    def get_catalog(self) -> Catalog:
        c = Catalog()
        c.vol('第一章')
        for i in range(100):
            c.chap(f'{i:0>3}', f't-[{i}]')

        return c


    def get_content(self, cid: str) -> str:
        time.sleep(0.1)
        return 'YESYESYES' + cid
