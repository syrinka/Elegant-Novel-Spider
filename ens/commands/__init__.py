from .dump import dump
from .dumper import dumper
from .fetch import fetch
from .info import info
from .local import local
from .remote import remote
from .utils import utils
from .web import web

def mount(entry):
    for cmd in (dump, dumper, fetch, info, local, remote, utils, web):
        entry.add_command(cmd)
