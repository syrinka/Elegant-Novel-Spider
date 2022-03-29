import time

from ens.remote import Remote, RemoteNovel
from ens.utils.remote import *


class Test(Remote):
    def get_info(self) -> RemoteNovel:
        return RemoteNovel(
            self.code, 'A Good Book {}'.format(self.code.nid),
            'Anonymous'
        )


    def get_catalog(self) -> Catalog:
        c = CatalogMaker()
        c.vol('第一章').chap('001').chap('002')
        return c.dump()


    def get_index(self) -> Dict[str, int]:
        return {'001': 'NUM-1', '002': 'NUM-2'}


    def get_content(self, cid: str) -> str:
        time.sleep(2)
        return 'YESYESYES'
