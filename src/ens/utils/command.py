import click

import ens.config as conf
from ens.console import echo
from ens.status import Status
from ens.remote import get_remote
from ens.dumper import get_dumper
from ens.typing import Code, FilterRule, ShelfFilter
from ens.paths import MANUAL, join
from ens.exceptions import *


def _code_callback(ctx, param, code):
    if code.startswith(conf.CODE_INDEX_INDICATOR):
        index = int(code.removeprefix(conf.CODE_INDEX_INDICATOR))

        stat = Status('sys')
        if index == 0 and conf.ZERO_MEANS_LAST:
            try:
                code = stat['last-cache']
            except KeyError:
                raise StatusError('last-cache not exists.')
                
        else:
            try:
                code = stat['shelf-cache'][index - 1]
            except IndexError:
                raise BadCodeIndex(len(stat['shelf-cache']), index)
            except KeyError:
                raise StatusError('shelf-cache not exists.')

    else:
        pass
    
    stat = Status('sys')
    stat.set('last-cache', code)
    stat.save()

    return Code(code)


arg_code = click.argument('code',
    metavar = 'CODE',
    callback = _code_callback
)


arg_remote = click.argument('remote',
    callback = lambda c, p, v: get_remote(v)
)


arg_dumper = click.argument('dumper',
    default = conf.DEFAULT_DUMPER,
    callback = lambda c, p, v: get_dumper(v)
)


def _filter_callback(ctx, param, rules):
    opt_rules = list(FilterRule(r) for r in rules)
    pos_rules = []
    for i in ('remote', 'title', 'author', 'intro'):
        rules = ctx.params.pop(i)
        for rule in rules:
            pos_rules.append(FilterRule(i + rule))

    mode = 'all' if ctx.params.pop('filter_mode') else 'any'

    return ShelfFilter(opt_rules + pos_rules, mode)


def opt_filter(cmd):
    # click option 的装饰器越靠内层的越后结算
    # 优先装饰 -f 以确保其最后结算，可以捕获到所有别名

    click.option('-f', '--filter',
        metavar = 'RULES',
        multiple = True,
        callback = _filter_callback,
        help = '根据给定条件进行筛选')(cmd)

    click.option('-R', '--remote',
        metavar='VALUE', multiple=True, hidden=True)(cmd)
    click.option('-T', '--title',
        metavar='VALUE', multiple=True, hidden=True)(cmd)
    click.option('-A', '--author',
        metavar='VALUE', multiple=True, hidden=True)(cmd)
    click.option('-I', '--intro',
        metavar='VALUE', multiple=True, hidden=True)(cmd)

    click.option('--all/--any', 'filter_mode',
        is_flag=True, default=True,
        hidden=True)(cmd)

    return cmd


def manual(mpage):
    def wrap(cmd):
        def get_help(ctx):
            path = join(MANUAL, mpage)
            text = open(path, encoding='utf-8').read()
            echo(text, nl=False)

        cmd.get_help = get_help
        return cmd
    return wrap
