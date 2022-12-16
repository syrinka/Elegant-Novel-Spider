import os
import click

from ens.console import echo
from ens.exceptions import LocalError
from ens.merge import edit
from ens.local import LocalCache, get_local_shelf, get_local_info
from ens.models import Shelf, Info
from ens.utils.click import manual, arg_novel, opt_filter, opt_pager


@manual('ens-local')
@click.group()
def local():
    """
    本地缓存 (Local) 管理
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
    列出所有本地缓存
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
        LocalCache.remove(novel)
        echo('删除成功')


@local.command('open')
@arg_novel
def func(novel):
    local = LocalCache(novel)
    os.startfile(local.path)


@local.command('info')
@arg_novel
@click.option('-e', '--edit', 'edit_',
    is_flag=True)
def func(novel, edit_):
    info = get_local_info(novel)
    if edit_:
        info = Info.load(edit(info.dump(), '.yml'))
    echo(info.verbose())


@local.command('show-catalog')
@arg_novel
@opt_pager
def func(novel, pager):
    local = LocalCache(novel)
    with pager:
        echo(local.catalog.dump())


@local.command('show-content')
@arg_novel
@click.argument('cid')
@opt_pager
def func(novel, cid, pager):
    local = LocalCache(novel)
    title = local.catalog.map[cid].title
    try:
        content = local.get_chap(cid)
    except KeyError:
        echo('[alert]章节数据不存在')
    with pager:
        echo(title)
        echo(content)


@local.command('edit-content')
@arg_novel
@click.argument('cid')
def func(novel, cid):
    local = LocalCache(novel)
    title = local.catalog.map[cid].title
    content = local.get_chap(cid)
    echo(f'Editing: {title}')
    
    local.set_chap(cid, edit(content))


@local.command('edit-catalog')
@arg_novel
def func(novel):
    local = LocalCache(novel)
    catalog = local.catalog
    edited = edit(catalog.dump())
    new_catalog = catalog.load(edited)
    local.update_catalog(catalog)
    echo('更新成功')


@local.command('insert-chapter')
@arg_novel
@click.argument('rel', type=click.Choice(['before', 'after']))
@click.argument('cid')
@click.argument('i_cid')
@click.argument('i_title')
def func(novel, rel, cid, i_cid, i_title):
    local = LocalCache(novel)
    old = local.catalog.dump()
    i = old.find('({})\n'.format(cid))
    if i == -1:
        raise LocalError('no such cid')

    if rel == 'before':
        while old[i] != '\n':
            i -= 1
    elif rel == 'after':
        while old[i] != '\n':
            i += 1

    new_cat = local.catalog.load(
        old[:i] + '\n. {} ({})'.format(i_title, i_cid) + old[i:]
    )

    new_chap = new_cat.map[i_cid]
    index = new_cat.spine.index(new_chap)
    try:
        before = new_cat.spine[index-1]
    except IndexError:
        before = '-- head --'
    try:
        after = new_cat.spine[index+1]
    except IndexError:
        after = '-- tail --'

    echo('新章节将插入于：')
    echo(before)
    echo(new_chap)
    echo(after)

    if not click.confirm('确定吗？'):
        raise click.Abort()

    content = edit('')
    local.set_chap(i_cid, content)
    local.update_catalog(new_cat)
    echo('inserted')


@local.command('star')
@arg_novel
def func(novel):
    local = LocalCache(novel)
    local.info.star = True
    local.update_info()


@local.command('unstar')
@arg_novel
def func(novel):
    local = LocalCache(novel)
    local.info.star = False
    local.update_info()


@local.command('isolate')
@arg_novel
def func(novel):
    local = LocalCache(novel)
    local.info.isolated = True
    local.update_info()


@local.command('unisolate')
@arg_novel
def func(novel):
    local = LocalCache(novel)
    local.info.isolated = False
    local.update_info()
