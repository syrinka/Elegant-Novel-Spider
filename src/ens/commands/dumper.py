import click

from ens.dumper import Dumper
from ens.console import echo


@click.group('dumper')
def main():
    """
    输出类型管理
    """
    pass


@main.command('list')
def func():
    """
    列出可用的输出类型
    """
    for i in Dumper.all_dumpers.keys():
        echo(i)
