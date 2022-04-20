import click

from ens.console import echo
from ens.remote import Remote
from ens.utils.command import arg_remote


@click.group('remote')
def main():
    """
    远程源 (Remote) 管理
    """
    pass


@main.command('list')
def func():
    """
    列出可用的远程源
    """
    for i in Remote.all_remotes.keys():
        echo(i)


@main.command('status')
@arg_remote
def func(remote: Remote):
    """
    检查远程源可用的功能
    """
    for feat, stat in remote.status().items():
        style = 'good' if stat else 'bad'
        echo(feat, style=style)
