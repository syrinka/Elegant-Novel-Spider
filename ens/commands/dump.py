import click

from ens.local import LocalStorage
from ens.paths import DUMP, join
from ens.utils.click import arg_novel, opt_dumper


@click.command(short_help='输出')
@arg_novel
@opt_dumper
@click.option('-o', '--output',
    type = str,
    help = '输出目标路径',
    default = '{title}{ext}',
    show_default = True)
def dump(novel, dumper, output, **kw):
    """
    输出小说
    """
    local = LocalStorage(novel)
    output = output.format(
        title = local.info.title,
        author = local.info.author,
        ext = dumper.ext or ''
    )
    output = join(DUMP, output)

    dumper.dump(
        local.info,
        local.catalog,
        local.get_chap,
        output
    )
