import click

from ens.local import get_local_shelf
from ens.console import echo
from ens.utils.command import *


@click.group('local')
def main():
    """
    本地数据 (Local) 管理
    """
    pass


@main.command('list')
@opt_filter
@click.option('-a', '--all',
    is_flag = True,
    help = '列出所有本地数据，包括无效的')
def func(filter, all):
    """
    列出所有本地数据
    """
    shelf = get_local_shelf(all)
    shelf.apply_filter(filter)
    shelf.cache_shelf()
    echo(shelf)
