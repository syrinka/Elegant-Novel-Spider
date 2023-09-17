## 模板

以下是一个远端源文件的模板

```python
from ens.remote import Remote
from ens.models import Catalog, RemoteInfo
from ens.console import log
from ens.utils.remote import CatalogBuilder


class RemoteExample(Remote):
    def get_info(self, nid: str) -> RemoteInfo:
        return RemoteInfo('title', 'author', 'intro', 'finish')


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

远端源文件应置于 `ens/remotes` 目录下。

每一个远端源继承于 `ens.remote.Remote`，并使用 `exports` 导出其名称。

`exports` 为元组，即 `Tuple[name, remote]`。一个文件也可以导出多个远端源，此时 `exports` 为字典 `Dict[name, remote]`。

## 依赖

推荐使用 `poetry add DEPENDENCY --group=REMOTE` 为每个远端源分别指定依赖。

这样可以 `poetry install --with=REMOTE` 安装特定远端源的依赖。

## 验证

使用 `python -m ens remote list` 与 `python -m ens remote status REMOTE` 以确认新的远端源能被正确识别。

若出现未知的错误，可尝试使用 debug 重试。
