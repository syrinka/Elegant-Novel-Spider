import click

from ens.console import echo
from ens.local import LocalStorage
from ens.paths import DUMP, join
from ens.utils.click import arg_novel, opt_dumper


@click.command(short_help='输出')
@arg_novel
@opt_dumper
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
    default = '{title}{ext}',
    show_default = True)
def dump(novel, dumper, miss, output, **kw):
    """
    输出小说
    """
    local = LocalStorage(novel)
    output = output.format(
        title = local.info.title,
        author = local.info.author,
        ext = dumper.ext or ''
    )


    dumper.dump(
        local.info,
        local.catalog,
        local.get_chap,
        output
    )
