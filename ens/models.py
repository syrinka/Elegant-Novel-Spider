from __future__ import annotations
import re
from dataclasses import dataclass, field, InitVar, asdict
from collections import namedtuple
from typing import (
    List, Dict, Tuple,
    Literal, Union
)

import yaml
from ens.config import config
from ens.status import Status
from ens.exceptions import (
    BadFilterRule, InvalidNovel
)


@dataclass
class Novel(object):
    remote: str
    nid: str


    def __repr__(self):
        return self.remote + config.CODE_DELIM + self.nid


    def __eq__(self, other):
        return repr(self) == (
            other if isinstance(other, str) \
            else repr(other)
        )


    def __iter__(self):
        return iter((self.remote, self.nid))


    def __rich__(self):
        return '[cyan]{}[/]{}[cyan]{}[/]'.format(
            self.remote, config.CODE_DELIM, self.nid
        )


@dataclass
class Info(object):
    novel: Novel
    
    title: str = None
    author: str = None
    intro: str = None
    finish: bool = None

    # metadata
    star: bool = False
    isolated: bool = False
    comment: str = None
    tags: list = field(default_factory=list)


    def __rich__(self):
        return '[green]{}[/]  [magenta]@{}[/] ({}) {} {}'.format(
            self.title,
            self.author or '[gray27]anon[/]', # anonymous
            self.novel.__rich__(),
            '[gray27]isolated[/]' if self.isolated else '',
            '[bright_yellow]★[/]' if self.star else ''
        )


    def __post_init__(self):
        # 使用 Info.load 载入数据时 novel 字段会成为 Dict 类型，这里修复之
        if isinstance(self.novel, dict):
            self.novel = Novel(**self.novel)


    def dump(self) -> str:
        return yaml.dump(asdict(self), allow_unicode=True, sort_keys=False)


    @classmethod
    def load(cls, data: str) -> Info:
        data = yaml.load(data, Loader=yaml.SafeLoader)
        return cls(**data)


    def verbose(self):
        return '{}\n\n[cyan]{}[/]'.format(
            self.__rich__(),
            (self.intro or 'no intro.').strip()
        )


@dataclass
class FilterRule(object):
    """
    @raise BadFilterRule
    """
    _rule_format = re.compile(
        r'(?P<attr>(?:remote)|(?:author)|(?:title)|(?:intro))'
        r'(?P<not>!?)(?P<mode>(?:[\^\@\*]?=)|)'
        r'(?P<value>.*)'
    )

    rule_str: InitVar[str]

    attr: Literal['remote', 'author', 'title', 'intro'] = field(init=False)
    mode: Literal['=', '==', '^=', '@=', '*='] = field(init=False)
    value: str = field(init=False)


    def __post_init__(self, rule_str):
        rule = self._rule_format.match(rule_str)
        if rule is None:
            raise BadFilterRule(rule_str)
        self.attr = rule['attr']
        self.mode = rule['mode'] or config.EMPTY_RULE_MODE
        self.value = rule['value']
        self.rev = bool(rule['not'])

    
    def compare(self, v0, v1) -> bool:
        if   self.mode == '=':  res = v1 in v0
        elif self.mode == '==': res = v0 == v1
        elif self.mode == '^=': res = v0.startswith(v1)
        elif self.mode == '@=': res = v0.endswith(v1)
        elif self.mode == '*=': res = v1 in v0
        return res ^ self.rev


    def __call__(self, info: Info) -> bool:
        v0 = getattr(info, self.attr)
        v1 = self.value
        return self.compare(v0, v1)

    def __repr__(self):
        return '{} {} {}'.format(
            self.attr, self.mode, self.value
        ) + (' (not)' if self.rev else '')


@dataclass
class Filter(object):
    rules: List[FilterRule]
    mode: Literal['all', 'any'] = 'all'


    def __call__(self, info) -> bool:
        judge = all if self.mode == 'all' else any
        return judge(rule(info) for rule in self.rules)

    
    def __repr__(self):
        return '\n'.join(str(rule) for rule in self.rules)


    def remote_in_scope(self, remote) -> bool:
        """
        判断某个远端源是否能通过过滤器
        在 get_local_shelf 时剔除必然被过滤的远端源，加快速度
        """
        for rule in self.rules:
            if rule.attr == 'remote':
                v0 = rule.value
                v1 = remote
                if not rule.compare(v0, v1):
                    return False
        return True


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
    def novels(self) -> List[Novel]:
        return list(n.novel for n in self.infos)


    def filter(self, ffunc: Filter, inplace=False):
        if inplace:
            self.infos = list(filter(ffunc, self.infos))
        else:
            return self.__class__(list(filter(ffunc, self.infos)))


    def cache_shelf(self):
        status = Status('ens')
        status.set('cache-shelf', [str(novel) for novel in self.novels])
        status.save()


    def dump(self):
        return [i.dump() for i in self.infos]


    @classmethod
    def load(cls, data):
        return cls([Info.load(d) for d in data])


@dataclass
class DumpMetadata(object):
    info: Info
    vol_count: int
    chap_count: int
    char_count: int
    path: str


Chapter = namedtuple('Chapter', 'cid title')

@dataclass
class Catalog(object):
    catalog: List[
        Dict[
            Literal['chaps', 'name'], Union[str, List[Chapter]]
        ]
    ]

    @property
    def index(self) -> Dict[str, str]:
        """{cid: title}"""
        if not hasattr(self, '_index'):
            index = dict(self.spine)
            self._index = index

        return self._index


    @property
    def spine(self) -> List[Chapter]:
        """Chapter(cid, title)"""
        if not hasattr(self, '_spine'):
            spine = []
            for vol in self.catalog:
                spine.extend(vol['chaps'])
            self._spine = spine

        return self._spine
            

    def dump(self) -> str:
        piece = []
        for vol in self.catalog:
            piece.append(f'# {vol["name"]}')
            for cid, title in vol['chaps']:
                piece.append(f'. {title} ({cid})')
        
        return '\n'.join(piece) + '\n'


    @classmethod
    def load(cls, data: str):
        catalog = []
        pattern = re.compile(r'. (?P<title>.+) \((?P<cid>.+)\)')
        for i in data.strip().split('\n'):
            if i.startswith('# '):
                catalog.append({
                    'name': i[2:],
                    'chaps': []
                })
            elif i.startswith('. '):
                m = pattern.match(i)
                catalog[-1]['chaps'].append(Chapter(m['cid'], m['title']))

        return cls(catalog)
