import click
from ens.api import api

@click.command()
@click.option('-d', '--debug',
    is_flag = True)
def web(debug):
    api.run('127.0.0.1', port=8000, debug=debug)
