import click

from ens.dumper import all_dumpers
from ens.console import echo


@click.group('dumper')
def main():
    """
    输出类型管理
    """
    pass


@main.command('list')
@click.option('--all', '-a',
    is_flag = True,
    help = '列出所有输出类型，包括不可用的')
def func(all):
    """
    列出可用的输出类型
    """
    for i in all_dumpers:
        if not all and all_dumpers[i]:
            echo(i)
        else:
            style = 'good' if all_dumpers[i] else 'bad'
            echo(i, style=style)

