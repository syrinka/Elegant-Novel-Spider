import re
from operator import attrgetter
from dataclasses import dataclass, field, InitVar, asdict
from datetime import datetime
from typing import (
    List, Dict, Tuple,
    Literal, Union,
    Type, NewType, Callable
)

import ens.config as conf
from ens.status import Status
from ens.exceptions import *


@dataclass
class Code(object):
    """
    Code('a~book') == Code(('a', 'book'))
    """
    _code_format = re.compile(
        r'([a-zA-Z0-9\-_\.]+)' + conf.CODE_DELIM + r'([a-zA-Z0-9\-_\.]+)'
    )

    init: InitVar[Union[str, Tuple]]

    remote: str = field(init=False)
    nid: str = field(init=False)


    def __repr__(self):
        return self.remote + conf.CODE_DELIM + self.nid


    def __eq__(self, other):
        return repr(self) == (
            other if isinstance(other, str) \
            else repr(other)
        )


    def __iter__(self):
        return iter((self.remote, self.nid))


    def __post_init__(self, init: Union[str, Tuple]):
        if isinstance(init, tuple):
            self.remote, self.nid = init

        else:
            match = self._code_format.match(init)
            if match is None:
                raise InvalidCode(init)

            self.remote, self.nid = match[1], match[2]


    def __rich__(self):
        return '[cyan]{}[/]{}[cyan]{}[/]'.format(
            self.remote, conf.CODE_DELIM, self.nid
        )


@dataclass
class Info(object):
    code: InitVar[Code]
    remote: str = field(init=False)
    nid: str = field(init=False)
    
    title: str = None
    author: str = None
    intro: str = ''
    tags: list = field(default_factory=list)
    last_update: datetime = None
    finish: bool = None


    def __post_init__(self, code):
        self.code = code
        self.remote, self.nid = code

        # 若刚初始化的本地数据未能 set_info，则标记为无效
        # 此时 title 仍为默认值 None
        self.valid = self.title is not None


    def __rich__(self):
        if not self.valid:
            return f'[gray27]\[invalid novel][/] ({self.code.__rich__()})'

        else:
            return '[green]{}[/]  [magenta]@{}[/] ({})'.format(
                self.title,
                self.author or '[gray27]anon[/]', # anonymous
                self.code.__rich__()
            )


    def dump(self) -> Dict:
        return asdict(self)


    @classmethod
    def load(cls, data):
        data['code'] = Code((data.pop('remote'), data.pop('nid')))
        return cls(**data)


    def verbose(self):
        if not self.valid:
            return self
        else:
            return '{}\n\n[cyan]{}[/]\n\n上次更新于：{}'.format(
                self.__rich__(),
                self.intro.strip() or 'no intro.',
                self.last_update or '----'
            )


@dataclass
class FilterRule(object):
    _rule_format = re.compile(
        r'(?P<attr>(?:remote)|(?:author)|(?:title)|(?:intro))'
        r'(?P<not>!?)(?P<mode>(?:[\^\@\*]?=)|)'
        r'(?P<value>.*)'
    )

    rule_str: InitVar[str]

    attr: Callable = field(init=False)
    mode: Literal['=', '==', '^=', '@=', '*='] = field(init=False)
    value: Literal['remote', 'author', 'title', 'intro'] = field(init=False)


    def __post_init__(self, rule_str):
        rule = self._rule_format.match(rule_str)
        if rule is None:
            raise BadFilter(rule_str)
        self.attr = rule['attr']
        self.aget = attrgetter(rule['attr'])
        self.mode = rule['mode'] or conf.EMPTY_RULE_MODE
        self.value = rule['value']
        self.rev = bool(rule['not'])


    def __call__(self, info: Info) -> bool:
        v0 = self.aget(info)
        v1 = self.value

        if   self.mode == '=':  res = v1 in v0
        elif self.mode == '==': res = v0 == v1
        elif self.mode == '^=': res = v0.startswith(v1)
        elif self.mode == '@=': res = v0.endswith(v1)
        elif self.mode == '*=': res = v1 in v0
        return res ^ self.rev

    def __repr__(self):
        return '{} {} {}'.format(
            self.attr, self.mode, self.value
        ) + (' (not)' if self.rev else '')


@dataclass
class ShelfFilter(object):
    rules: List[FilterRule]
    mode: Literal['all', 'any'] = 'all'


    def __call__(self, info) -> bool:
        judge = all if self.mode == 'all' else any
        return judge(rule(info) for rule in self.rules)

    
    def __repr__(self):
        return '\n'.join(str(rule) for rule in self.rules)


@dataclass
class Shelf(object):
    infos: List[Info] = field(default_factory=list)


    def __add__(self, info):
        self.infos.append(info)
        return self


    def __rich_console__(self, console, opt):
        for i, info in enumerate(self.infos):
            yield '#{}  {}'.format(i+1, info.__rich__())


    @property
    def codes(self) -> List[Code]:
        return list(n.code for n in self.infos)


    def filter(self, ffunc: ShelfFilter, inplace=False):
        if inplace:
            self.infos = list(filter(ffunc, self.infos))
        else:
            return self.__class__(list(filter(ffunc, self.infos)))


    def cache_shelf(self):
        status = Status('sys')
        status.set('shelf-cache', [str(code) for code in self.codes])
        status.save()


    def dump(self):
        return [i.dump() for i in self.infos]


    @classmethod
    def load(cls, data):
        return cls([Info.load(d) for d in data])



class Catalog(object):
    """
    c = Catalog()
    c.vol(...)
    c.chap(...)
    c.chap(...)
    """
    def __init__(self) -> None:
        self.catalog = list()
        self.index = {}
        self.access = {}


    def vol(self, name: str):
        self.catalog.append({'name': name, 'cids': []})
        return self


    def chap(self, cid: str, title: str, access=None):
        self.catalog[-1]['cids'].append(cid)
        self.index[cid] = title
        if access is not None:
            self.access = access
        return self


@dataclass
class DumpMetadata(object):
    info: Info
    vol_count: int
    chap_count: int
    char_count: int
    path: str


if __name__ == '__main__':
    a = Info('a~b', 'A', 'B')
    print(a)
