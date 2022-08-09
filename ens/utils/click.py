import re
import click

from ens import __version__
from ens.config import config
from ens.console import echo, pager
from ens.cache import Cache
from ens.remote import get_remote
from ens.dumper import get_dumper
from ens.models import Novel, FilterRule, Filter
from ens.paths import MANUAL, join
from ens.exceptions import *


def translate_novel(novel: str) -> str:
    if novel.startswith(config.CODE_INDEX_INDICATOR):
        try:
            index = int(novel.removeprefix(config.CODE_INDEX_INDICATOR))
        except ValueError:
            raise InvalidNovel(novel)

        cache = Cache('ens')
        if index == 0:
            try:
                return cache['cache-last']
            except KeyError:
                raise CacheError('cache-last not exists.')
                
        else:
            try:
                return cache['cache-shelf'][index - 1]
            except IndexError:
                raise CacheError(f'Cache index out of range, max index {len(cache["cache-shelf"])-1}')
            except KeyError:
                raise CacheError('cache-shelf not exists.')

    else:
        return novel


def _novel_callback(ctx, param, novel):
    format = re.compile(r'([a-zA-Z0-9\-_\.]+)' + config.CODE_DELIM + r'([a-zA-Z0-9\-_\.]+)')
    novel = translate_novel(novel)

    m = format.match(novel)
    if m is None:
        raise InvalidNovel(novel)

    cache = Cache('ens')
    cache.set('cache-last', novel)
    cache.save()
    return Novel(m[1], m[2])


arg_novel = click.argument('novel',
    metavar = 'NOVEL',
    callback = _novel_callback
)


arg_remote = click.argument('remote',
    callback = lambda c, p, v: get_remote(v)
)


opt_dumper = click.option('-d', '--dumper',
    default = config.DEFAULT_DUMPER,
    metavar = 'DUMPER',
    help = '选择输出类型，详见 docs:dump',
    show_default = True,
    callback = lambda c, p, v: get_dumper(v),
)


def _filter_callback(ctx, param, rules):
    opt_rules = list(FilterRule(r) for r in rules)
    pos_rules = []
    for i in ('remote', 'title', 'author', 'intro'):
        rules = ctx.params.pop(i)
        for rule in rules:
            pos_rules.append(FilterRule(i + rule))

    mode = 'all' if ctx.params.pop('filter_mode') else 'any'

    return Filter(opt_rules + pos_rules, mode)


def opt_filter(cmd):
    click.option('-f', '--filter',
        metavar = 'RULE',
        multiple = True,
        callback = _filter_callback,
        help = '根据给定条件进行筛选，详见 docs:filter')(cmd)

    click.option('-R', '--remote',
        is_eager = True, metavar='VALUE', multiple=True, hidden=True)(cmd)
    click.option('-T', '--title',
        is_eager = True, metavar='VALUE', multiple=True, hidden=True)(cmd)
    click.option('-A', '--author',
        is_eager = True, metavar='VALUE', multiple=True, hidden=True)(cmd)
    click.option('-I', '--intro',
        is_eager = True, metavar='VALUE', multiple=True, hidden=True)(cmd)

    click.option('--all/--any', 'filter_mode',
        is_eager = True, is_flag=True, default=True,
        hidden=True)(cmd)

    return cmd


class _fake_pager(object):
    def __enter__(self):
        pass


    def __exit__(self, *args):
        pass


def _pager_callback(ctx, param, value):
    if value:
        return pager()
    else:
        return _fake_pager()


def opt_pager(cmd):
    click.option('-p', '--pager',
        is_flag=True, callback=_pager_callback)(cmd)
    return cmd


def manual(mpage):
    def wrap(cmd):
        # hack
        def get_help(ctx):
            path = join(MANUAL, mpage)
            text = open(path, encoding='utf-8').read().format(
                version=__version__
            )
            echo(text, nl=False)

        cmd.get_help = get_help
        return cmd
    return wrap
