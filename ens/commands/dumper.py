import click

from ens import echo, Dumper


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
    for i in Dumper.all_dumpers.keys():
        echo(i)
