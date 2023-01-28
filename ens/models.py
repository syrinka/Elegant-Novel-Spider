from __future__ import annotations
import re
from dataclasses import dataclass, field, InitVar, asdict
from typing import (
    List, Dict, Literal, 
    Union, Optional,
    NamedTuple
)

import yaml
from ens.config import config


# hack yaml style
# turn multi line string into "|" style
def str_presenter(dumper, data):
    scaler = dumper.represent_scalar(u'tag:yaml.org,2002:str', data)
    if len(data.splitlines()) >= 2:
        scaler.style = '|'
    return scaler

yaml.add_representer(str, str_presenter)
# to use with safe_dump:
yaml.representer.SafeRepresenter.add_representer(str, str_presenter)


class Chapter(NamedTuple):
    cid: str
    title: str

    def __str__(self):
        return '{} ({})'.format(self.title, self.cid)

class Volume(NamedTuple):
    title: str
    chaps: List[Chapter]

class NavPoint(NamedTuple):
    type: Literal['vol', 'chap']
    title: str
    index: Optional[int]


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
    
    title: Optional[str] = None
    author: Optional[str] = None
    intro: Optional[str] = None
    finish: Optional[bool] = None
    tags: List[str] = field(default_factory=list)

    # metadata
    star: bool = False
    isolated: bool = False
    comment: Optional[str] = None


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
        items = [
            self.__rich__(),
            ('[cyan]' + self.intro + '[/]') \
                if self.intro else None,
            ' '.join(f'\[{tag}]' for tag in self.tags) \
                if self.tags else None,
            ('[purple]' + self.comment  + '[/]') \
                if self.comment else None
        ]
        return '\n\n'.join(item for item in items if item is not None)


@dataclass
class Info_(object):
    """Info directly returned from `get_info()`
    """
    title: Optional[str] = None
    author: Optional[str] = None
    intro: Optional[str] = None
    finish: Optional[bool] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class FilterRule(object):
    """
    Raises:
        ValueError: illegal rule expression
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
            raise ValueError(rule_str)
        self.attr = rule['attr']
        self.mode = rule['mode'] or config.EMPTY_RULE_MODE
        self.value = rule['value']
        self.rev = bool(rule['not'])

    
    def compare(self, v0, v1) -> bool:
        if   self.mode == '=':  res = v1 in v0
        elif self.mode == '==': res = v0 == v1
        elif self.mode == '^=': res = v0.startswith(v1)
        elif self.mode == '$=': res = v0.endswith(v1)
        elif self.mode == '*=': res = v1 in v0
        return res ^ self.rev


    def __call__(self, info: Info) -> bool:
        if self.attr == 'remote':
            v0 = info.novel.remote
        else:
            v0 = getattr(info, self.attr)
        v1 = self.value
        return self.compare(v0, v1)

    def __repr__(self):
        return '{} {} {}'.format(
            self.attr, self.mode, self.value
        ) + (' (not)' if self.rev else '')


@dataclass
class Filter(object):
    rules: Union[List[FilterRule], None] # 若传入 None，则该过滤器永远返回 True
    mode: Literal['all', 'any'] = 'all'


    def __call__(self, info) -> bool:
        if self.rules is None:
            return True
        else:
            judge = all if self.mode == 'all' else any
            return judge(rule(info) for rule in self.rules)

    
    def __repr__(self):
        return '\n'.join(str(rule) for rule in self.rules)


    def is_remote_in_scope(self, remote) -> bool:
        """
        判断某个远端源是否能通过过滤器，若能通过，返回 True

        在 get_local_shelf 时首先剔除必然被过滤的远端源，加快速度
        """
        if self.rules is None:
            return True
        else:
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
            yield config.CODE_INDEX_INDICATOR + '{}  {}'.format(i+1, info.__rich__())


    @property
    def novels(self) -> List[Novel]:
        return list(n.novel for n in self.infos)


    def dump(self):
        return [i.dump() for i in self.infos]


    @classmethod
    def load(cls, data):
        return cls([Info.load(d) for d in data])


@dataclass
class Catalog(object):
    catalog: List[Volume]

    @property
    def map(self) -> Dict[str, Chapter]:
        if not hasattr(self, '_map'):
            map = {chap.cid: chap for chap in self.spine}
            self._map = map

        return self._map


    @property
    def spine(self) -> List[Chapter]:
        """Chapter(cid, title)"""
        if not hasattr(self, '_spine'):
            spine = []
            for vol in self.catalog:
                spine.extend(vol.chaps)
            self._spine = spine

        return self._spine


    def nav_list(self) -> List[NavPoint]:
        """用于供网页生成有层次的目录"""
        nav = []
        index = 0
        for vol in self.catalog:
            nav.append(NavPoint('vol', vol.title, None))
            for chap in vol.chaps:
                nav.append(NavPoint('chap', chap.title, index))
                index += 1
        return nav


    def __sub__(self, other: Catalog) -> List[Chapter]:
        delta = []
        for i in self.map:
            if i not in other.map:
                delta.append(self.map[i])
        return delta
            

    def dump(self) -> str:
        piece = []
        for vol in self.catalog:
            piece.append(f'# {vol.title}')
            for chap in vol.chaps:
                piece.append(f'. {chap.title} ({chap.cid})')
        
        return '\n'.join(piece) + '\n'


    @classmethod
    def load(cls, data: str) -> Catalog:
        #TODO 检测是否为合法的输入
        catalog: List[Volume] = []
        pattern = re.compile(r'. (?P<title>.+) \((?P<cid>.+)\)')
        for i in data.strip().split('\n'):
            if i.startswith('# '):
                catalog.append(Volume(i[2:], []))
            elif i.startswith('. '):
                m = pattern.match(i)
                catalog[-1].chaps.append(Chapter(m['cid'], m['title']))

        return cls(catalog)
