import click
from ens.api import api

@click.command('web')
@click.option('-d', '--debug',
    is_flag = True)
def main(debug):
    api.run('127.0.0.1', port=8000, debug=debug)
