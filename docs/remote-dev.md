# 编写新的远端源
以下是一个远端源的模板

```python
from ens.remote import Remote
from ens.typing import Info, Catalog
from ens.console import log
from ens.exceptions import GetContentFail, FetchError


class Template(Remote):
    def get_info(self, code) -> Info:
        return Info(
            code, 'title', 'author', 'intro', 'finish'
        )


    def get_catalog(self) -> Catalog:
        c = Catalog()

        for vol in get_vols():
            c.vol(vol.name)
            for chap in vol.get_chaps():
                c.chap(chap.cid, chap.title)

        return c


    def get_content(self, code, cid: str) -> str:
        return 'text'.strip()

```
