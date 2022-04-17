import click

from ens.console import echo
from ens.status import Status
from ens.utils.command import arg_code, opt_filter


@click.group('util')
def main():
    pass


@main.command('code')
@arg_code
def func(code):
    """
    测试 code 的解析结果
    """
    echo(code)


@main.command('filter')
@opt_filter
def func(filter):
    """
    测试 filter 的解析结果
    """
    echo(filter)


@main.command('code-cache')
def func():
    """
    last-cache and shelf-cache
    """
    stat = Status('sys')
    echo('# last-cache')
    echo(stat['last-cache'])
    echo('# shelf-cache')
    for i, code in enumerate(stat['shelf-cache']):
        echo(f'{i+1} {code}')
