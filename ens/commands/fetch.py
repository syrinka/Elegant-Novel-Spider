from threading import Thread, Lock
from time import sleep

import click

from ens.console import echo, log, doing, Track
from ens.models import Novel, Info
from ens.local import LocalStorage
from ens.remote import get_remote
from ens.merge import catalog_lose, merge_catalog, merge
from ens.utils.click import arg_novel
from ens.exceptions import (
    FetchError,
    GetContentFail,
    LocalNotFound,
    RemoteNotFound,
    MergeError,
    Abort
)


@click.command()
@arg_novel
@click.option('--info', 'update_info',
    is_flag = True,
    help = '只更新 info')
@click.option('-m', '--mode',
    type = click.Choice(['update', 'flush', 'diff']),
    default = 'update',
    help = '''\b
    处理数据的方式
    - update 只抓取缺失章节，不改变已保存的章节 [default]
    - flush  抓取全部章节并覆盖 !dangerous!
    - diff   抓取全部章节，如为已保存章节，则对比差异''')
@click.option('-i', '--interval',
    type = click.FloatRange(min=0),
    default = 0.2,
    help = '抓取间隔（秒）[0.2]')
@click.option('-r', '--retry',
    type = click.IntRange(min=0),
    default = 3,
    help = '抓取单章时最大尝试次数，为 0 则持续尝试 [3]')
@click.option('-t', '--thread', # TODO 多线程执行
    type = click.IntRange(min=2),
    default = None,
    hidden = True,
    help = '同时执行的线程数')
def fetch(novel: Novel, update_info: bool, mode: str, interval: float, retry: int, thread: int):
    """
    抓取小说
    """
    if mode=='diff' and thread is not None:
        raise FetchError('暂不支持 mode=diff 与多线程的组合')

    try:
        remote = get_remote(novel.remote)()
    except RemoteNotFound:
        raise

    try:
        local = LocalStorage(novel)
        echo(local.info)

        if update_info:
            try:
                with doing('Getting Info'):
                    info = remote.get_info(novel)
            except FetchError as e:
                echo(e)
                echo('抓取 Info 失败')
                #TODO raise Isolated(novel) 

            old = local.info.dump()
            new = info.dump()
            merged = merge(old, new)
            info = Info.load(merged)
            local.update_info(info)

            echo('Info 更新成功！')
            return

    except LocalNotFound:
        log('local initialize')

        local = LocalStorage.init(novel)
        try:
            with doing('Getting Info'):
                info = remote.get_info(novel)
        except FetchError as e:
            echo(e)
            echo('[alert]抓取 Info 失败')
            del local
            LocalStorage.remove(novel)
            raise Abort

        echo(info.verbose())
        if not click.confirm('是这本吗？', default=True):
            del local
            LocalStorage.remove(novel)
            raise Abort

        local.update_info(info) # 更新信息

    try:
        with doing('Getting catalog'):
            new_cat = remote.get_catalog(novel)
    except FetchError:
        raise FetchError('Fail to get catalog.')

    # merge catalog
    old_cat = local.catalog
    if catalog_lose(old_cat, new_cat):
        echo('[alert]检测到目录发生了减量更新，即将进行手动合并')
        try:
            new_cat = merge_catalog(old_cat, new_cat)
        except MergeError:
            echo('放弃合并，本次抓取终止')
            raise Abort

    local.update_catalog(new_cat)

    chaps = [chap for chap in new_cat.spine]
    if mode == 'update':
        # 如为 update 模式，则只抓取缺失章节
        chaps = [chap for chap in chaps if not local.has_chap(chap.cid)]

    def save(local: LocalStorage, cid, content):
        if mode == 'update':
            local.set_chap(cid, content)

        elif mode == 'flush':
            local.set_chap(cid, content)

        elif mode == 'diff':
            old = local.get_chap(cid)
            if old != content:
                title = local.get_title(cid)
                echo(f'检测到章节内容变动：{title} ({cid})')
                try:
                    content = merge(old, content)
                except MergeError:
                    echo('[yellow]放弃合并，章节内容未变动')
                else:
                    echo('[green]合并完成')
                    local.set_chap(cid, content)

    track = Track(chaps, 'Fetching')
    if thread is None:
        for chap in track:
            track.update_desc(chap.title)

            try:
                content = remote.get_content(novel, chap.cid)
            except FetchError as e:
                echo(e)
                continue

            save(local, chap.cid, content)

    else:
        chaps = iter(track)
        sync = Lock()
        def worker():
            local = LocalStorage(novel)
            while True:
                try:
                    with sync:
                        chap = next(chaps)

                    track.update_desc(local.get_title(chap.cid))
                    try:
                        content = remote.get_content(novel, chap.cid)
                    except GetContentFail as e:
                        echo(e)
                        continue
                    save(local, chap.cid, content)

                except StopIteration:
                    break

        threads = [Thread(target=worker) for i in range(thread)]
        log('{} threads online'.format(thread))

        try:
            for th in threads:
                th.setDaemon(True)
                th.start()
            while True:
                sleep(0.5)
                stat = 0
                for th in threads:
                    stat |= th.is_alive()
                if not stat:
                    break
        except KeyboardInterrupt:
            raise Abort

    echo('Done.', style='good')
