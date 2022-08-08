import click

from ens import echo, Dumper
from ens.dumper import get_dumper, get_dumper_list


@click.group()
def dumper():
    """
    输出类型管理
    """
    pass


@dumper.command('list')
def func():
    """
    列出可用的输出类型
    """
    for i in get_dumper_list():
        echo(i)
