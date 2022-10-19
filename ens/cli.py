import sys
import click
from loguru import logger

from ens.config import config
from ens.commands import mount
from ens.utils.click import manual


@manual('ens')
@click.group('ens')
@click.option('-l', '--log-level',
    type=int)
@click.option('-d', '--debug', 'log_level',
    type=int,
    flag_value=10)
@click.pass_context
def ens_cli(ctx, log_level):
    ctx.info_name = 'ens'
    
    level = log_level or config.LOG_LEVEL or 0
    logger.remove()
    if level:
        logger.add(sys.stderr, level=level)
    logger.debug('log level: %d' % level)

mount(ens_cli)
