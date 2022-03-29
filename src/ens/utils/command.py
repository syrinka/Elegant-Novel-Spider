import click

import ens.config as conf
from ens.typing import Code
from ens.status import Status
from ens.remote import get_remote
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
    type = str,
    callback = _code_callback
)


def _remote_callback(ctx, param, remote):
    try:
        return get_remote(remote)
    except RemoteNotFound:
        raise


arg_remote = click.argument('remote',
    type = str,
    callback = _remote_callback
)


opt_all = lambda h: click.option('--all', '-a',
    is_flag = True,
    help = h
)


def alias(entry: click.Group, alias, origin):
    entry.commands[alias] = entry.commands[origin]
