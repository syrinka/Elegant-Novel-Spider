import click
from ens.api import api

@click.command('gui')
def main():
    api.run('127.0.0.1', port=8000, debug=True)
