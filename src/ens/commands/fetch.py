from threading import Thread, Lock

import click

from ens.local import Local
from ens.remote import get_remote
from ens.console import echo, log, doing, Track
from ens.merge import catalog_lose, merge_catalog, merge
from ens.utils import yaml_load, yaml_dump
from ens.utils.command import arg_code
from ens.typing import *
from ens.exceptions import *


@click.command('fetch')
@arg_code
@click.option('--info',
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
def main(code: Code, info: bool, mode: str, interval: float, retry: int, thread: int):
    """
    抓取小说
    """
    try:
        remote = get_remote(code.remote)(code)
    except RemoteNotFound:
        raise

    try:
        local = Local(code)
        echo(local.info)

        if info:
            try:
                with doing('Getting Info'):
                    info = remote.get_info()
            except FetchError:
                raise FetchError('Fail to get remote info.')

            old = yaml_dump(local.info.dump())
            new = yaml_dump(info.dump())
            merged = merge(old, new)
            info = Info.load(yaml_load(merged))
            local.set_info(info)

            echo('Info 更新成功！')
            return

    except LocalNotFound:
        log('local initialize')

        local = Local.init(code)
        try:
            with doing('Getting Info'):
                info = remote.get_info()
        except FetchError as e:
            echo(e)
            echo('[alert]抓取 Info 失败')
            del local
            Local.remove(code)
            raise Abort

        echo(info.verbose())
        if not click.confirm('是这本吗？', default=True):
            del local
            Local.remove(code)
            raise Abort

        local.set_info(info) # 更新信息

    try:
        with doing('Getting catalog'):
            cat = remote.get_catalog()
    except FetchError:
        raise FetchError('Fail to get catalog.')

    # merge catalog
    if catalog_lose(local.catalog, cat.catalog):
        echo('[alert]检测到目录发生了减量更新，即将进行手动合并')
        index = local.get_index()
        try:
            cat.catalog = merge_catalog(local.catalog, cat.catalog, index)
        except MergeError:
            echo('放弃合并，本次抓取终止')
            raise Abort

    local.set_catalog(cat)

    cids = [cid for cid in local.spine()]
    if mode == 'update':
        # 如为 update 模式，则只抓取缺失章节
        cids = [cid for cid in cids if not local.has_chap(cid)]

    def save(local, cid, content):
        if mode == 'update':
            local.set_chap(cid, content)

        elif mode == 'flush':
            local.set_chap(cid, content)

        elif mode == 'diff':
            raise NotImplementedError('Not support for now!') # TODO

    track = Track(cids, 'Fetching')
    if thread is None:
        for cid in track:
            track.update_desc(local.get_title(cid))

            try:
                content = remote.get_content(cid)
            except FetchError as e:
                echo(e)
                continue

            save(local, cid, content)

    else:
        cids = iter(track)
        sync = Lock()
        def worker():
            local = Local(code)
            while True:
                try:
                    with sync:
                        cid = next(cids)

                    track.update_desc(local.get_title(cid))
                    try:
                        content = remote.get_content(cid)
                    except FetchError as e:
                        echo(e)
                        continue
                    save(local, cid, content)

                except StopIteration:
                    break

        threads = [Thread(target=worker) for i in range(thread)]
        echo('{} threads online'.format(thread))
        for th in threads:
            th.start()
        for th in threads:
            th.join()

    echo('Done.', style='good')
