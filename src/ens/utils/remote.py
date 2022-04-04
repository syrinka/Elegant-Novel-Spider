from ens.typing import *


class CatalogMaker(object):
    """
    c = CatalogMaker()
    c.vol(...)
    c.chap(...)
    c.chap(...)
    """
    def __init__(self) -> None:
        self.catalog = list()
        self.index = {}


    def vol(self, name: str):
        self.catalog.append({'name': name, 'cids': []})
        return self


    def chap(self, cid: str, title: str):
        self.catalog[-1]['cids'].append(cid)
        self.index[cid][title]
        return self


    def dump(self) -> Catalog:
        return self.catalog
