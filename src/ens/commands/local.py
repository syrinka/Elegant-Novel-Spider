import click

from ens import echo, edit
from ens import Local, Shelf, get_local_shelf, get_local_info
from ens.merge import flatten
from ens.utils.command import manual, arg_code, opt_filter, opt_pager


@manual('ens-local')
@click.group('local')
def main():
    """
    本地库 (Local) 管理
    """
    pass


@main.command('list')
@opt_filter
@click.option('-s', '--star',
    is_flag = True,
    help = 'Starred only.')
def func(filter, star):
    """
    列出所有本地库
    """
    shelf = get_local_shelf(filter)
    if star:
        shelf = Shelf(list(i for i in shelf.infos if i.star))

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


@main.command('info')
@arg_code
def func(code):
    info = get_local_info(code)
    echo(info.verbose())


@main.command('show-catalog')
@arg_code
@opt_pager
def func(code, pager):
    local = Local(code)
    with pager:
        echo(flatten(local.catalog(), local.get_index()))


@main.command('show-content')
@arg_code
@click.argument('cid')
@opt_pager
def func(code, cid, pager):
    local = Local(code)
    title = local.get_title(cid)
    content = local.get_chap(cid)
    with pager:
        echo(title)
        echo(content)


@main.command('edit-content')
@arg_code
@click.argument('cid')
def func(code, cid):
    local = Local(code)
    title = local.get_title(cid)
    content = local.get_chap(cid)
    echo(f'Editing: {title}')
    
    local.set_chap(cid, edit(content))


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
