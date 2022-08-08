import click

import ens.config as conf
from ens.commands import mount
from ens.utils.click import manual


@manual('ens')
@click.group('ens')
@click.option('-d', '--debug',
    is_flag = True)
@click.pass_context
def ens_cli(ctx, debug):
    ctx.info_name = 'ens'
    if debug:
        conf.DEBUG = debug

mount(ens_cli)
