import pkgutil
import click
import ens.commands as cmds


@click.group('ens')
def ens_cli():
    pass


for ff, name, ispkg in pkgutil.iter_modules(cmds.__path__, ):
    if (name not in cmds.disabled) and (not name.startswith('_')):
        name = 'ens.commands.' + name # as fullname
        main = ff.find_module(name).load_module(name).main
        ens_cli.add_command(main)
