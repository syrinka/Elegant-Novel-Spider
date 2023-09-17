from threading import Lock, Thread
from time import sleep
from typing import List

import click

from ens.console import Track, console, doing, echo, logger
from ens.exceptions import Abort, ExternalError
from ens.local import LocalStorage
from ens.merge import catalog_lose, merge, merge_catalog
from ens.models import LocalInfo, Novel, RemoteInfo
from ens.remote import get_remote
from ens.utils.click import arg_novels, manual


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
    except KeyError:
        raise

    try:
        local = LocalStorage(novel)
        echo(local.info)

        if fetch_info:
            try:
                with doing('Getting Info'):
                    info = remote.get_info(novel.nid)
                    info = LocalInfo.from_remote(info, local.info)
            except Exception as e:
                echo('[alert]爬取 Info 失败')
                if isinstance(e, FileNotFoundError):
                    echo('预期的资源不存在，可能已被删除')
                raise e

            old = local.info.dump()
            new = info.dump()
            merged = merge(old, new)
            info = LocalInfo.load(merged)
            local.update_info(info)

            echo('Info 更新成功！')
            return

    except KeyError:
        logger.debug('local initialize')

        local = LocalStorage.new(novel)
        try:
            with doing('Getting Info'):
                info = remote.get_info(novel.nid)
        except Exception as e:
            echo('[alert]爬取 Info 失败，未捕获的异常，请检查爬虫逻辑')
            del local
            LocalStorage.remove(novel)
            if isinstance(e, FileNotFoundError):
                echo('预期的资源不存在，可能已被删除')
            raise e

        echo(info.verbose())
        if not click.confirm('是这本吗？', default=True):
            del local
            LocalStorage.remove(novel)
            raise Abort

        local.update_info(info) # 更新信息

    try:
        with doing('Getting catalog'):
            new_cat = remote.get_catalog(novel.nid)
    except Exception as e:
        echo('[alert]爬取 Catalog 失败')
        if isinstance(e, FileNotFoundError):
            echo('预期的资源不存在，可能已被删除')
        raise e

    # merge catalog
    old_cat = local.catalog
    if catalog_lose(old_cat, new_cat):
        echo('[alert]检测到目录发生了减量更新，即将进行手动合并')
        try:
            new_cat = merge_catalog(old_cat, new_cat)
        except ExternalError:
            echo('放弃合并，本次爬取终止')
            raise Abort

    local.update_catalog(new_cat)

    merge_lock = Lock()
    def resolve(chap):
        cid, title = chap
        track.update_desc(title)
        try:
            content = remote.get_content(novel.nid, cid)
        except Exception as e:
            echo(e)
            return

        if mode in ('update', 'flush'):
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
        logger.debug('{} threads online'.format(thnum))

        try:
            for th in threads:
                th.start()
            while True: # 使用主线程轮询以正确处理 SIGINT 信号
                sleep(0.5)
                if alive_count == 0:
                    logger.debug('all threads exited')
                    break
        except KeyboardInterrupt:
            interrupt = True # 设置终止 flag
            echo('等待所有线程退出中')
            for th in threads: # 等待线程全部退出
                th.join()
            raise Abort

    echo('Done.', style='good')
