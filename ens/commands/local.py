import click

from ens.console import echo, edit
from ens.local import LocalStorage, get_local_shelf, get_local_info
from ens.models import Shelf
from ens.utils.click import manual, arg_novel, opt_filter, opt_pager


@manual('ens-local')
@click.group()
def local():
    """
    本地库 (Local) 管理
    """
    pass


@local.command('list')
@opt_filter
@click.option('-s', '--star',
    is_flag = True,
    help = 'Starred only.')
@opt_pager
def func(filter, star, pager):
    """
    列出所有本地库
    """
    shelf = get_local_shelf(filter)
    if star:
        shelf = Shelf(list(i for i in shelf.infos if i.star))

    shelf.cache_shelf()
    with pager:
        echo(shelf)


@local.command('remove')
@arg_novel
@click.option('-y', '--yes',
    is_flag = True,
    help = '确定确定确定')
def func(novel, yes):
    info = get_local_info(novel)
    echo(info.verbose())
    if yes or click.confirm('确定要删除它吗？'):
        LocalStorage.remove(novel)
        echo('删除成功')


@local.command('info')
@arg_novel
def func(novel):
    info = get_local_info(novel)
    echo(info.verbose())


@local.command('show-catalog')
@arg_novel
@opt_pager
def func(novel, pager):
    local = LocalStorage(novel)
    with pager:
        echo(local.catalog.dump())


@local.command('show-content')
@arg_novel
@click.argument('cid')
@opt_pager
def func(novel, cid, pager):
    local = LocalStorage(novel)
    title = local.get_title(cid)
    content = local.get_chap(cid)
    with pager:
        echo(title)
        echo(content)


@local.command('edit-content')
@arg_novel
@click.argument('cid')
def func(novel, cid):
    local = LocalStorage(novel)
    title = local.get_title(cid)
    content = local.get_chap(cid)
    echo(f'Editing: {title}')
    
    local.set_chap(cid, edit(content))


@local.command('star')
@arg_novel
def func(novel):
    local = LocalStorage(novel)
    local.info.star = True
    local.set_info()


@local.command('unstar')
@arg_novel
def func(novel):
    local = LocalStorage(novel)
    local.info.star = False
    local.set_info()


@local.command('isolate')
@arg_novel
def func(novel):
    local = LocalStorage(novel)
    local.info.isolated = True
    local.set_info()


@local.command('unisolate')
@arg_novel
def func(novel):
    local = LocalStorage(novel)
    local.info.isolated = False
    local.set_info()
