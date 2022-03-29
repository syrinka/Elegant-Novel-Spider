import click

from ens.local import Local, get_local_shelf
from ens.console import echo
from ens.utils.command import *


@click.group('local')
def main():
    """
    本地数据 (Local) 管理
    """
    pass


@main.command('list')
def func():
    """
    列出所有本地数据

    Alias: ls
    """
    shelf = get_local_shelf()
    echo(shelf)


alias(main, 'ls', 'list')
