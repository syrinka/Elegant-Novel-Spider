import click

from ens import echo, get_local_info, get_remote
from ens.utils.command import arg_code


@click.command('info')
@arg_code
@click.option('-l/-r', '--local/--remote', 'local',
    is_flag = True,
    default = True,
    help = '查看本地/远程信息')
def main(code, local):
    if local:
        info = get_local_info(code)
    else:
        remote = get_remote(code.remote)()
        info = remote.get_info()

    echo(info.verbose())