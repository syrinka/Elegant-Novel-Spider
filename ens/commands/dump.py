import click

from ens.console import echo
from ens.local import LocalStorage
from ens.paths import DUMP, join
from ens.models import DumpMetadata
from ens.exceptions import ChapMissing
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

    meta = DumpMetadata(
        local.info,
        local.catalog,
        join(DUMP, output)
    )

    dumper = dumper()
    dumper.init(meta)

    for vol in local.catalog():
        dumper.feed('vol', vol['name'])

        for cid in vol['cids']:
            try:
                title = local.get_title(cid)
                content = local.get_chap(cid)
            except ChapMissing:
                if miss == 'skip':
                    continue

                elif miss == 'stop':
                    echo(f'[alert]章节数据缺失[/] {title} ({cid})')
                    echo('[fatal]输出已中止')
                    break
                
                elif miss == 'warn':
                    echo(f'[alert]章节数据缺失[/] {title} ({cid})')
                    continue

            dumper.feed('chap', (title, content))

    dumper.dump()
