import click

from ens.console import echo
from ens.local import get_local_info
from ens.remote import get_remote
from ens.utils.click import arg_novel


@click.command()
@arg_novel
@click.option('-l/-r', '--local/--remote', 'local',
    is_flag = True,
    default = True,
    help = '查看本地/远程信息')
def info(novel, local):
    if local:
        info = get_local_info(novel)
    else:
        remote = get_remote(novel.remote)()
        info = remote.get_info(novel)

    echo(info.verbose())