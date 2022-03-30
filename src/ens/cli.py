import pkgutil
import click
import ens.commands as cmds

from ens.utils.command import manual


@manual('ens')
@click.group('ens')
@click.pass_context
def ens_cli(ctx):
    ctx.info_name = 'ens'


for ff, name, ispkg in pkgutil.iter_modules(cmds.__path__, ):
    if (name not in cmds.disabled) and (not name.startswith('_')):
        name = 'ens.commands.' + name # as fullname
        main = ff.find_module(name).load_module(name).main
        ens_cli.add_command(main)
