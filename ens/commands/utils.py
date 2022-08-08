import click

from ens import echo, log, Status
from ens.utils.command import arg_code, opt_filter, translate_code


@click.group()
def utils():
    pass


@utils.command('code')
@arg_code
def func(code):
    """
    测试 code 的解析结果
    """
    echo(code)


@utils.command('filter')
@opt_filter
def func(filter):
    """
    测试 filter 的解析结果
    """
    echo(filter)
