# 编写新的远端源
以下是一个远端源的模板

```python
from ens.remote import Remote
from ens.models import Info, Catalog
from ens.console import log
from ens.utils.remote import CatalogBuilder
from ens.exceptions import FetchError


class Template(Remote):
    def get_info(self, novel) -> Info:
        return Info(
            novel, 'title', 'author', 'intro', 'finish'
        )


    def get_catalog(self) -> Catalog:
        c = CatalogBuilder()

        for vol in get_vols():
            c.vol(vol.name)
            for chap in vol.get_chaps():
                c.chap(chap.cid, chap.title)

        return c.build()


    def get_content(self, novel, cid: str) -> str:
        return 'text'.strip()

```
