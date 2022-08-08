import click

from ens.console import echo, log
from ens.cache import Cache
from ens.utils.click import arg_novel, opt_filter, translate_novel


@click.group()
def utils():
    pass


@utils.command('novel')
@arg_novel
def func(novel):
    """
    测试 novel 的解析结果
    """
    echo(novel)


@utils.command('filter')
@opt_filter
def func(filter):
    """
    测试 filter 的解析结果
    """
    echo(filter)
