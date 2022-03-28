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


    def vol(self, name: str):
        self.catalog.append({'name': name, 'cids': []})


    def chap(self, cid: str):
        self.catalog[-1]['cids'].append(cid)


    def dump(self) -> Catalog:
        return self.catalog
