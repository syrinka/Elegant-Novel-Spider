import click

from ens.utils.command import *


@click.group('test')
def main():
    pass


@main.command('code')
@arg_code
def func(code):
    print(code)
