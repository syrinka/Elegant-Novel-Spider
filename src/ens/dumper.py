import pkgutil

import ens.dumpers as dumpers
from ens.local import Local
from ens.exceptions import *
from ens.typing import *


class Dumper(object):
    _dumpers = dict()
    name = None

    def __init_subclass__(cls) -> None:
        cls.name = cls.name or cls.__name__.lower()
        if cls.name in cls._remotes:
            raise DuplicateRemote(cls.name)
        cls._remotes[cls.name] = cls


    def feed(self, type: Literal['meta', 'vol', 'chap'], data):
        """
        meta: DumpMetadata
        vol: str
        chap: title, content
        """
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
