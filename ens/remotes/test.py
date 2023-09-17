from ens.models import Catalog, RemoteInfo
from ens.remote import Remote
from ens.utils.remote import CatalogBuilder


class Test(Remote):
    def get_info(self, nid: str) -> RemoteInfo:
        return Info(
            '示例书目 {}'.format(nid),
            '群星',
            'nothing here',
        )


    def get_catalog(self, nid: str) -> Catalog:
        c = CatalogBuilder()

        c.vol('第一卷')
        for i in range(10):
            c.chap(i, 'No.{}'.format(i))

        return c.build()


    def get_content(self, nid: str, cid: str) -> str:
        return 'Text at chapter {}'.format(cid)


exports = ('test', Test)
