import click

from ens.utils.command import arg_code
from ens.local import get_local_info
from ens.remote import get_remote
from ens.console import echo


@click.command('info')
@arg_code
@click.option('-l/-r', '--local/--remote', 'local',
    is_flag = True,
    default = True)
def main(code, local):
    if local:
        info = get_local_info(code)
    else:
        remote = get_remote(code.remote)(code)
        info = remote.get_info()

    echo(info.verbose())