from threading import Thread, Lock
from time import sleep
from typing import List

import click

from ens.console import console, echo, log, doing, Track
from ens.models import Novel, Info
from ens.local import LocalCache
from ens.remote import get_remote
from ens.merge import catalog_lose, merge_catalog, merge
from ens.utils.click import arg_novels, manual
from ens.exceptions import (
    FetchError,
    DataNotFound,
    LocalNotFound,
    RemoteNotFound,
    ExternalError,
    MaybeIsolated
)


@manual('ens-fetch')
@click.command()
@arg_novels
@click.option('--fetch-info',
    is_flag = True)
@click.option('-m', '--mode',
    type = click.Choice(['update', 'flush', 'diff', 'patch']),
    default = 'update')
@click.option('-r', '--retry',
    type = click.IntRange(min=0),
    default = 3)
@click.option('-t', '--thread', 'thnum', # TODO 多线程执行
    type = click.IntRange(min=2),
    default = None)
def fetch(novels: List[Novel], **kw):
    """
    爬取小说
    """
    for novel in novels:
        fetch_novel(novel, **kw)


def fetch_novel(novel: Novel, fetch_info: bool, mode: str, retry: int, thnum: int):
    try:
        remote = get_remote(novel.remote)
    except RemoteNotFound:
        raise

    try:
        local = LocalCache(novel)
        echo(local.info)

        if fetch_info:
            try:
                with doing('Getting Info'):
                    info = remote.get_info(novel)
            except FetchError as e:
                echo('[alert]爬取 Info 失败')
                if isinstance(e, DataNotFound):
                    raise MaybeIsolated()
                else:
                    raise e

            # 同步一些本地独立信息
            #TODO refactor
            info.star = local.info.star
            info.isolated = local.info.isolated
            info.comment = local.info.comment

            old = local.info.dump()
            new = info.dump()
            merged = merge(old, new)
            info = Info.load(merged)
            local.update_info(info)

            echo('Info 更新成功！')
            return

    except LocalNotFound:
        log('local initialize')

        local = LocalCache.new(novel)
        try:
            with doing('Getting Info'):
                info = remote.get_info(novel)
        except FetchError as e:
            echo(e)
            echo('[alert]爬取 Info 失败')
            del local
            LocalCache.remove(novel)
            raise click.Abort
        except Exception as e:
            console.print_exception()
            echo('[alert]爬取 Info 失败，未捕获的异常，请检查爬虫逻辑')
            del local
            LocalCache.remove(novel)
            raise click.Abort

        echo(info.verbose())
        if not click.confirm('是这本吗？', default=True):
            del local
            LocalCache.remove(novel)
            raise click.Abort

        local.update_info(info) # 更新信息

    try:
        with doing('Getting catalog'):
            new_cat = remote.get_catalog(novel)
    except FetchError as e:
        echo('[alert]爬取 Info 失败')
        if isinstance(e, DataNotFound):
            raise MaybeIsolated()
        else:
            raise e

    # merge catalog
    old_cat = local.catalog
    if catalog_lose(old_cat, new_cat):
        echo('[alert]检测到目录发生了减量更新，即将进行手动合并')
        try:
            new_cat = merge_catalog(old_cat, new_cat)
        except ExternalError:
            echo('放弃合并，本次爬取终止')
            raise click.Abort

    local.update_catalog(new_cat)
    
    merge_lock = Lock()
    def resolve(chap):
        cid, title = chap
        track.update_desc(title)
        try:
            content = remote.get_content(novel, cid)
        except FetchError as e:
            echo(e)
            return

        if mode == 'update' or mode == 'flush':
            local.set_chap(cid, content)

        elif mode == 'diff':
            try:
                old = local.get_chap(cid)
            except KeyError:
                # 是新章节，直接保存
                local.set_chap(cid, content)     
                return

            if old != content:
                merge_lock.acquire()
                echo(f'检测到章节内容变动：{title} ({cid})')
                try:
                    content = merge(old, content)
                except ExternalError:
                    echo('[yellow]放弃合并，章节内容未变动')
                else:
                    echo('[green]合并完成')
                    local.set_chap(cid, content)
                merge_lock.release()

        elif mode == 'patch':
            try:
                old = local.get_chap(cid)
            except KeyError:
                # 是新章节，直接保存
                local.set_chap(cid, content)     
                return           

            if old in content:
                print(chap.title)
                local.set_chap(cid, content)
                return


    chaps = [chap for chap in new_cat.spine]
    if mode == 'update':
        # 如为 update 模式，则在此处筛去本地已保存章节
        chaps = [chap for chap in chaps if not local.has_chap(chap.cid)]

    track = Track(chaps, 'Fetching')
    if thnum is None:
        for chap in track:
            resolve(chap)

    else:
        alive_count = thnum
        interrupt = False
        chaps = iter(track)
        sync = Lock()
        def worker():
            nonlocal alive_count
            while True:
                if interrupt:
                    return

                try:
                    with sync:
                        chap = next(chaps) # 保护生成器线程安全
                    
                    resolve(chap)

                except StopIteration:
                    with sync:
                        alive_count -= 1
                    break

        threads = [Thread(target=worker, daemon=True) for i in range(thnum)]
        log('{} threads online'.format(thnum))

        try:
            for th in threads:
                th.start()
            while True: # 使用主线程轮询以正确处理 SIGINT 信号
                sleep(0.5)
                if alive_count == 0:
                    break
        except KeyboardInterrupt:
            interrupt = True # 设置终止 flag
            echo('等待所有线程退出中')
            for th in threads: # 等待线程全部退出
                th.join()
            raise click.Abort

    echo('Done.', style='good')
