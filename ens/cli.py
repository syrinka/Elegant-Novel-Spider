import pkgutil
import click
import ens.commands as cmds

import ens.config as conf
from ens.utils.command import manual


@manual('ens')
@click.group('ens')
@click.option('-d', '--debug',
    is_flag = True)
@click.pass_context
def ens_cli(ctx, debug):
    ctx.info_name = 'ens'
    if debug:
        conf.DEBUG = debug


for ff, name, ispkg in pkgutil.iter_modules(cmds.__path__, ):
    if (name not in cmds.disabled) and (not name.startswith('_')):
        name = 'ens.commands.' + name # as fullname
        main = ff.find_module(name).load_module(name).main
        ens_cli.add_command(main)
