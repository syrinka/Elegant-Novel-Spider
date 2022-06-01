import pkgutil
from warnings import warn
from typing import Type, Literal

import ens.dumpers as dumpers
from ens.typing import DumpMetadata
from ens.exceptions import DumperNotFound


class Dumper(object):
    all_dumpers = dict()
    ext = None

    def __init_subclass__(cls) -> None:
        name = cls.__module__.rsplit('.', 1)[-1]
        if name in cls.all_dumpers:
            warn(f'Duplicate dumper {name}, may lead to unexpected behaviour.')
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
