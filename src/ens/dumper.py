import pkgutil

import ens.dumpers as dumpers
from ens.exceptions import *
from ens.typing import *


class Dumper(object):
    _dumpers = dict()
    name = None

    def __init_subclass__(cls) -> None:
        cls.name = cls.name or cls.__name__.lower()
        if cls.name in cls._dumpers:
            raise DuplicateDumper(cls.name)
        cls._dumpers[cls.name] = cls


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
        return Dumper._dumpers[name]
    except KeyError:
        raise DumperNotFound(name)


all_dumpers = {}
for ff, name, ispkg in pkgutil.iter_modules(dumpers.__path__):
    if name not in dumpers.disabled:
        all_dumpers[name] = True
        name = 'ens.dumpers.' + name
        ff.find_module(name).load_module(name)
    else:
        all_dumpers[name] = False
