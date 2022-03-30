import click

from ens.local import Local, get_novel
from ens.dumper import get_dumper, all_dumpers
from ens.paths import DUMP, join
from ens.typing import *
from ens.utils.command import *


def _list_callback(ctx, param, value):
    if value:
        for i, status in all_dumpers.items():
            if status:
                echo(i)
        ctx.exit()


def _dumper_callback(ctx, param, value):
    print('yes')
    return value


@click.command('dump', short_help='输出')
@arg_code
@click.option('-l', '--list', 'ls',
    is_flag = True,
    callback = _list_callback,
    help = '列出所有可用的 dumper')
@click.option('-d', '--dumper',
    callback = _dumper_callback)
@click.option('--txt', 'dumper',
    flag_value = 'txt',
    default = True,
    help = '以 txt 形式输出',)
@click.option('--epub', 'dumper',
    flag_value = 'epub',
    help = '以 epub 形式输出')
@click.option('-m', '--miss',
    type = click.Choice(['skip', 'stop', 'warn']),
    default = 'stop',
    help = '''\b
    控制出现章节数据缺失时的行为
      skip 跳过
      stop 警告并终止 [default]
      warn 警告并跳过''')
@click.option('-o', '--output',
    type = str,
    help = '输出目标路径',
    default = '{title}.{ext}',
    show_default = True)
def main(code, dumper, miss, output, **kw):
    """
    输出小说
    """
    print(dumper)
    return
    local = Local(code)

    dumper = get_dumper(dumper)
    init = DumpInitData(
        get_novel(code),
        local.get_meta(),
        join(DUMP, output)
    )

    dumper = dumper(init)
