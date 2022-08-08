import click

from ens import echo, Remote
from ens.utils.command import arg_remote


@click.group()
def remote():
    """
    远程源 (Remote) 管理
    """
    pass


@remote.command('list')
def func():
    """
    列出可用的远程源
    """
    for i in Remote.all_remotes.keys():
        echo(i)


@remote.command('status')
@arg_remote
def func(remote: Remote):
    """
    检查远程源可用的功能
    """
    for feat, stat in remote.status().items():
        style = 'good' if stat else 'bad'
        echo(feat, style=style)
