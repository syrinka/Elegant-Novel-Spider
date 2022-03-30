import click

import ens.config as conf
from ens.console import echo
from ens.status import Status
from ens.remote import Remote, get_remote
from ens.dumper import Dumper, get_dumper
from ens.typing import Code, Shelf, FilterRule, ShelfFilter
from ens.paths import MANUAL, join
from ens.exceptions import *


def _code_callback(ctx, param, code):
    if code.startswith(conf.CODE_INDEX_INDICATOR):
        index = int(code.removeprefix(conf.CODE_INDEX_INDICATOR))

        stat = Status('sys')
        if index == 0 and conf.ZERO_MEANS_LAST:
            try:
                code = stat['last-code']
            except KeyError:
                raise StatusError('last-code not exists.')
                
        else:
            try:
                code = stat['cache-codes'][index - 1]
            except IndexError:
                raise BadCodeIndex(len(stat['cache-codes']), index)
            except KeyError:
                raise StatusError('cache-codes not exists.')

        return Code(code)

    else:
        return Code(code)


arg_code = click.argument('code',
    metavar = 'CODE',
    callback = _code_callback
)


arg_remote = click.argument('remote',
    metavar = 'REMOTE',
    callback = lambda c, p, v: get_remote(v)
)


opt_dumper = click.option('-d', '--dumper',
    metavar = 'DUMPER',
    default = 'txt',
    callback = lambda c, p, v: get_dumper(v)
)


opt_all = click.option('--all', '-a',
    is_flag = True
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


def alias(entry: click.Group, alias, origin):
    entry.commands[alias] = entry.commands[origin]


def manual(mpage):
    def wrap(cmd):
        def get_help(ctx):
            path = join(MANUAL, mpage)
            text = open(path, encoding='utf-8').read()
            echo(text, nl=False)

        cmd.get_help = get_help
        return cmd
    return wrap
