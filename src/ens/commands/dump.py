import click

from ens.local import Local, get_novel
from ens.dumper import Dumper, all_dumpers
from ens.paths import DUMP, join
from ens.typing import *
from ens.utils.command import *
from ens.exceptions import *


def _list_callback(ctx, param, value):
    if value:
        for i, status in all_dumpers.items():
            if status:
                echo(i)
        ctx.exit()


@click.command('dump', short_help='输出')
@arg_code
@click.option('-l', '--list', 'ls',
    is_flag = True,
    callback = _list_callback,
    help = '列出所有可用的 dumper')
@opt_dumper
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
def main(code, dumper: Dumper, miss, output, **kw):
    """
    输出小说
    """
    local = Local(code)
    meta = DumpMetadata(
        get_novel(code),
        local.vol_count(),
        local.chap_count(),
        local.chap_count(),
        join(DUMP, output)
    )

    dumper = dumper()
    dumper.feed('meta', meta)

    for vol in local.catalog:
        dumper.feed('vol', vol['name'])

        for cid in vol['cids']:
            title = local.get_chap_title(cid)
            content = local.get_chap(cid)
            dumper.feed('chap', (title, content))

    dumper.dump()
