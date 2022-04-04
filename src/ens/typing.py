import re
from operator import attrgetter
from dataclasses import dataclass, field, InitVar, asdict
from typing import List, Dict, Tuple, Literal, Union, NewType, Type, Callable
from datetime import datetime

import ens.config as conf
from ens.status import Status
from ens.exceptions import *


@dataclass
class Code(object):
    _code_format = re.compile(
        r'([a-zA-Z0-9\-_\.]+)' + conf.CODE_DELIM + r'([a-zA-Z0-9\-_\.]+)'
    )

    code_str: InitVar[str]

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


    def __post_init__(self, code_str: str):
        match = self._code_format.match(code_str)
        if match is None:
            raise InvalidCode(code_str)

        self.remote, self.nid = match[1], match[2]


    def __rich__(self):
        return '[plum4]{}[/]{}[cyan]{}[/]'.format(
            self.remote, conf.CODE_DELIM, self.nid
        )


@dataclass
class Novel(object):
    remote: str
    nid: str
    title: str
    author: str
    intro: str = None
    last_update: datetime = None


    def __rich__(self):
        return '[green]{}[/]  [magenta]@{}[/] ({})'.format(
            self.title, self.author, self.code.__rich__()
        )


    @property
    def code(self) -> Code:
        return Code(self.remote + conf.CODE_DELIM + self.nid)


    def as_dict(self):
        return asdict(self)


@dataclass
class FilterRule(object):
    _rule_format = re.compile(
        r'(?P<attr>(?:remote)|(?:author)|(?:title)|(?:intro))'
        r'(?P<not>!?)(?P<mode>(?:[\^\@\*]?=)|)'
        r'(?P<value>.*)'
    )

    rule_str: InitVar[str]

    attr: Callable = field(init=False)
    mode: Literal['=', '^=', '@=', '*='] = field(init=False)
    value: Literal['remote', 'author', 'title', 'intro'] = field(init=False)


    def __post_init__(self, rule_str):
        rule = self._rule_format.match(rule_str)
        self.attr = rule['attr']
        self.aget = attrgetter(rule['attr'])
        self.mode = rule['mode'] or conf.EMPTY_RULE_MODE
        self.value = rule['value']
        self.rev = bool(rule['not'])


    def __call__(self, novel: Novel) -> bool:
        v0 = self.aget(novel)
        v1 = self.value

        if   self.mode == '=':  res = v0 == v1
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


    def __call__(self, novel) -> bool:
        judge = all if self.mode == 'all' else any
        return judge(rule(novel) for rule in self.rules)

    
    def __repr__(self):
        return '\n'.join(str(rule) for rule in self.rules)


@dataclass
class Shelf(object):
    name: Union[str, None] = None
    novels: List[Novel] = field(default_factory=list)


    def __add__(self, novel):
        self.novels.append(novel)
        return self


    def __rich_console__(self, console, opt):
        if self.name is not None:
            yield f'\[{self.name}]'
        for i, novel in enumerate(self.novels):
            yield '#{}  {}'.format(i+1, novel.__rich__())


    @property
    def codes(self) -> List[Code]:
        return list(n.code for n in self.novels)


    def apply_filter(self, ffunc: ShelfFilter):
        self.novels = list(filter(ffunc, self.novels))


    def cache_shelf(self):
        status = Status('sys')
        status.set('shelf-cache', [str(code) for code in self.codes])
        status.save()


@dataclass
class RemoteNovel(object):
    code: Code
    title: str
    author: str
    intro: str = ''
    chap_count: int = None
    tags: set = field(default_factory=set)
    point: float = None
    fav: int = None
    last_update: datetime = None
    finish: bool = None
    expand: dict = field(default_factory=dict)


    def __rich__(self):
        text = ''
        def push(i='', style=None, nl=True):
            nonlocal text
            if style:
                text += '[{}]{}[/]'.format(style, i)
            else:
                text += i
            if nl:
                text += '\n'

        push('{}'.format(self.title), 'green', nl=False)
        if self.point != None:
            push(' <{}>'.format(self.point), 'yellow', nl=False)
        if self.fav != None:
            push(' ♥{}'.format(self.fav), 'bright_red', nl=False)
        push()
        if self.author is not None:
            push(self.author, 'bright_magenta')
        else:
            push('佚名')
        if self.chapters != None:
            push('{}章'.format(self.chap_count))
        if self.tags:
            push(' '.join('[{}]'.format(tag.strip()) for tag in self.tags))
        else:
            push('No tag')
        push(self.intro or 'No intro', 'cyan')
        for i, j in self.expand.items():
            push('{}: {}'.format(i, j))
        if self.last_update is not None:
            push('最后一次更新于 {}'.format(self.last_update))
        if self.finish:
            push('已完结', 'green')
        return text[:-1] # 去掉最后一个换行符


    def as_novel(self) -> Novel:
        return Novel(
            self.code.remote, self.code.nid,
            self.title, self.author, self.intro, self.last_update
        )


class Catalog(object):
    """
    c = Catalog()
    c.vol(...)
    c.chap(...)
    c.chap(...)
    """
    def __init__(self) -> None:
        self.catalog = list()
        self._index = {}


    def vol(self, name: str):
        self.catalog.append({'name': name, 'cids': []})
        return self


    def chap(self, cid: str, title: str):
        self.catalog[-1]['cids'].append(cid)
        self._index[cid] = title
        return self


    def get_index(self):
        return self._index


@dataclass
class DumpMetadata(object):
    info: Novel
    vol_count: int
    chap_count: int
    char_count: int
    path: str


if __name__ == '__main__':
    pass
