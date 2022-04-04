import click

from ens.utils.command import arg_code
from ens.local import get_novel
from ens.remote import get_remote
from ens.console import echo


@click.command('info')
@arg_code
@click.option('-l/-r', '--local/--remote', 'local',
    is_flag = True,
    default = True)
def main(code, local):
    if local:
        novel = get_novel(code)
        echo(novel.verbose())
    else:
        remote = get_remote(code.remote)
        echo(remote(code).get_info().verbose())
