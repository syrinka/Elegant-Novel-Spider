import click

from ens.utils.command import arg_code, opt_filter


@click.group('test')
def main():
    pass


@main.command('code')
@arg_code
def func(code):
    """
    测试 code 的解析结果
    """
    print(code)


@main.command('filter')
@opt_filter
def func(filter):
    """
    测试 filter 的解析结果
    """
    print(filter)
