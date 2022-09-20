import click

from ens.console import echo
from ens.merge import merge, edit
from ens.state import State
from ens.utils.click import arg_novel, opt_filter


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


@utils.command('merge')
@click.argument('text1')
@click.argument('text2')
def func(text1, text2):
    """
    测试 merge 的结果
    """
    echo(merge(text1, text2))


@utils.command('edit')
@click.argument('text')
def func(text):
    """
    测试 merge 的结果
    """
    echo(edit(text))
