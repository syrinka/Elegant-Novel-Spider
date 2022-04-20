import pkgutil

import ens.dumpers as dumpers
from ens.exceptions import *
from ens.typing import *


class Dumper(object):
    all_dumpers = dict()
    ext = None

    def __init_subclass__(cls) -> None:
        name = cls.__module__.rsplit('.', 1)[-1]
        if name in cls.all_dumpers:
            raise DuplicateDumper(name)
        cls.all_dumpers[name] = cls


    def init(self, meta: DumpMetadata):
        pass


    def feed(self, type: Literal['vol', 'chap'], data):
        """
        vol: str
        chap: title, content
        """
        pass


    def dump(self):
        pass


    def abort(self):
        pass


def get_dumper(name) -> Type[Dumper]:
    try:
        return Dumper.all_dumpers[name]
    except KeyError:
        raise DumperNotFound(name)


for ff, name, ispkg in pkgutil.iter_modules(dumpers.__path__):
    name = 'ens.dumpers.' + name
    ff.find_module(name).load_module(name)
