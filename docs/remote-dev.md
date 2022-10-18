# 模板

以下是一个远端源的模板

```python
from ens.remote import Remote
from ens.models import Info_ as Info, Catalog
from ens.console import log
from ens.utils.remote import CatalogBuilder
from ens.exceptions import FetchError


class RemoteExample(Remote):
    def get_info(self, nid: str) -> Info:
        return Info('title', 'author', 'intro', 'finish')


    def get_catalog(self, nid: str) -> Catalog:
        c = CatalogBuilder()

        for vol in get_vols():
            c.vol(vol.name)
            for chap in vol.get_chaps():
                c.chap(chap.cid, chap.title)

        return c.build()


    def get_content(self, nid: str, cid: str) -> str:
        return 'text'.strip()


exports = ('example', RemoteExample)
```

新的远端源应置于 `ens/remotes` 目录下，文件名为远端源名。

使用 `python -m ens remote list` 与 `python -m ens remote status REMOTE` 以确认新的远端源能被正确识别。

## 依赖

我们推荐使用 `poetry add DEPENDENCY --group=REMOTE` 为每个远端源指定独立的依赖
