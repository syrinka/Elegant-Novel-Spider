import click

from ens.console import echo
from ens.remote import Remote, all_remotes
from ens.utils.command import *


@click.group('remote')
def main():
    """
    远程源 (Remote) 管理
    """
    pass


@main.command('list')
@click.option('-a', '--all',
    is_flag = True,
    help = '列出所有远程源，包括不可用的')
def func(all):
    """
    列出可用的远程源
    """
    for i in all_remotes:
        if not all and all_remotes[i]:
            echo(i)
        else:
            style = 'good' if all_remotes[i] else 'bad'
            echo(i, style=style)


@main.command('status')
@arg_remote
def func(remote: Remote):
    """
    检查远程源可用的功能
    """
    for feat, stat in remote.status().items():
        style = 'good' if stat else 'bad'
        echo(feat, style=style)
