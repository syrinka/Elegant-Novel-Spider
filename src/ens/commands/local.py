import click

from ens.local import Local, get_local_shelf, get_local_info
from ens.console import echo
from ens.utils.command import arg_code, opt_filter


@click.group('local')
def main():
    """
    本地库 (Local) 管理
    """
    pass


@main.command('list')
@opt_filter
def func(filter):
    """
    列出所有本地库
    """
    shelf = get_local_shelf()
    shelf = shelf.filter(filter)
    shelf.cache_shelf()
    echo(shelf)


@main.command('remove')
@arg_code
@click.option('-y', '--yes',
    is_flag = True,
    help = '确定确定确定')
def func(code, yes):
    info = get_local_info(code)
    echo(info.verbose())
    if yes or click.confirm('确定要删除它吗？'):
        Local.remove(code)
        echo('删除成功')


@main.command('star')
@arg_code
def func(code):
    local = Local(code)
    local.info.star = True
    local.set_info()


@main.command('unstar')
@arg_code
def func(code):
    local = Local(code)
    local.info.star = False
    local.set_info()


@main.command('isolate')
@arg_code
def func(code):
    local = Local(code)
    local.info.isolated = True
    local.set_info()


@main.command('unisolate')
@arg_code
def func(code):
    local = Local(code)
    local.info.isolated = False
    local.set_info()
