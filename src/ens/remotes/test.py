import time

from ens.remote import Remote, RemoteNovel
from ens.typing import Catalog


class Test(Remote):
    def get_info(self) -> RemoteNovel:
        return RemoteNovel(
            self.code, 'A Good Book {}'.format(self.code.nid),
            'Anonymous'
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
