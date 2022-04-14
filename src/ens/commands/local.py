import click

from ens.local import Local, get_local_shelf, get_local_info
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
    shelf = shelf.filter(filter)
    shelf.cache_shelf()
    echo(shelf)


@main.command('remove')
@arg_code
@click.option('-y', '--yes',
    is_flag = True,
    help = '确定确定确定')
def func(code, yes):
    info = get_local_info(code)
    echo(info.verbose())
    if yes or click.confirm('确定要删除它吗？'):
        Local.remove(code)
        echo('删除成功')
