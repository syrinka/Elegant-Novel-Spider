from typing import List
from ens.models import Catalog, Chapter, Volume


class CatalogBuilder(object):
    """
    c = Catalog()
    c.vol(...)
    c.chap(...)
    c.chap(...)
    """
    def __init__(self):
        self.catalog: List[Volume] = []


    def vol(self, title: str):
        title = str(title)
        self.catalog.append(Volume(title, []))
        return self


    def chap(self, cid: str, title: str):
        cid = str(cid)
        title = str(title)
        self.catalog[-1].chaps.append(Chapter(cid, title))
        return self


    def build(self) -> Catalog:
        return Catalog(self.catalog)
