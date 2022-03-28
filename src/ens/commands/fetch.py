import click

from ens.local import Local
from ens.remote import get_remote
from ens.typing import *
from ens.exceptions import *


@click.command('fetch')
def main(code: Code):
    try:
        remote = get_remote(code.remote)(code)
    except RemoteNotFound:
        return # alert

    try:
        local = Local(code)
    except LocalNotFound:
        local = Local.init(code)

    try:
        r_novel = remote.get_novel()
    except FetchFail:
        return

    novel = r_novel.as_novel()
    # merge novel info

    local.set_novel(novel) # 更新信息

    try:
        catalog = remote.get_catalog()
    except FetchFail:
        return

    # merge catalog

    local.set_catalog(catalog)

    try:
        index = remote.get_index()
    except FetchFail:
        return

    local.set_index(index)

    cids = [cid for cid in local.spine() if (cid not in local)]
    for cid in cids:
        remote.get_content(cid)
        


