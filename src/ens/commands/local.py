import click

from ens.utils.command import *


@click.group('local')
def main():
    """
    本地数据 (Local) 管理
    """
    pass


@main.command('list')
def func(all):
    """
    列出所有本地数据

    Alias: ls
    """
    pass


alias(main, 'ls', 'list')
