import click

from ens.console import echo
from ens.local import get_local_info
from ens.remote import get_remote
from ens.utils.click import arg_code


@click.command()
@arg_code
@click.option('-l/-r', '--local/--remote', 'local',
    is_flag = True,
    default = True,
    help = '查看本地/远程信息')
def info(code, local):
    if local:
        info = get_local_info(code)
    else:
        remote = get_remote(code.remote)()
        info = remote.get_info(code)

    echo(info.verbose())