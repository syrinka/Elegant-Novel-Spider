import click

from ens.cli import ens_cli
from ens import echo, log, Status
from ens.utils.command import arg_code, opt_filter, translate_code


@click.group('util')
def main():
    pass


@main.command('code')
@arg_code
def func(code):
    """
    测试 code 的解析结果
    """
    echo(code)


@main.command('filter')
@opt_filter
def func(filter):
    """
    测试 filter 的解析结果
    """
    echo(filter)


@main.command('batch-exec')
@click.argument('exec',
    required = False,
    nargs = -1)
@click.option('-c', '--code', 'codes',
    multiple = True)
@click.option('-s', '--stop',
    is_flag = True,
    help = 'Stop at first exception.')
@click.option('-n', '--dry',
    is_flag = True)
def func(exec, codes, stop, dry):
    """
    对批量小说执行同一个命令
    """
    for code in codes:
        code = translate_code(code)

        cmd = ' '.join(exec) + ' ' + code
        echo(f'batch exec: [green]{cmd}')

        if not dry:
            try:
                ens_cli.main(exec + (code,), standalone_mode=False)
            except Exception as e:
                echo(e)
                if stop:
                    break
