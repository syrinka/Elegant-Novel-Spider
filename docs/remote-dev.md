# 编写新的远端源
以下是一个远端源的模板

```python
from ens.remote import Remote
from ens.models import Info, Catalog, Novel
from ens.console import log
from ens.utils.remote import CatalogBuilder
from ens.exceptions import FetchError


class RemoteExample(Remote):
    def get_info(self, novel: Novel) -> Info:
        return Info(
            novel, 'title', 'author', 'intro', 'finish'
        )


    def get_catalog(self, novel: Novel) -> Catalog:
        c = CatalogBuilder()

        for vol in get_vols():
            c.vol(vol.name)
            for chap in vol.get_chaps():
                c.chap(chap.cid, chap.title)

        return c.build()


    def get_content(self, novel: Novel, cid: str) -> str:
        return 'text'.strip()


export = ExampleRemote
```

新的远端源应置于 `ens/remotes` 目录下，文件名为远端源名。

使用 `python -m ens remote list` 与 `python -m ens remote status REMOTE` 以确认远端源已正确被识别。
