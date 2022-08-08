from ens.models import Catalog, Chapter


class CatalogBuilder(object):
    """
    c = Catalog()
    c.vol(...)
    c.chap(...)
    c.chap(...)
    """
    def __init__(self):
        self.catalog = list()


    def vol(self, name: str):
        self.catalog.append({'name': name, 'chaps': []})
        return self


    def chap(self, cid: str, title: str):
        self.catalog[-1]['chaps'].append(Chapter(cid, title))
        return self


    def build(self) -> Catalog:
        return Catalog(self.catalog)
