import os
import tempfile
import subprocess
from contextlib import contextmanager

from rich.console import Console
from rich.theme import Theme
from rich.progress import (
    Progress,
    SpinnerColumn,
    TimeRemainingColumn,
    BarColumn
)

from ens.config import DEBUG
from ens.paths import APP
from ens.exceptions import *


__all__ = [
    'console',
    'doing',
    'log',
    'echo',
    'run',
    'pager',
    'Track'
]


theme = Theme({
    'bad': 'red',
    'good': 'green',
    'alert': 'yellow',
    'fatal': 'red'
})
console = Console(highlight=False, theme=theme)


doing = console.status


def log(*obj):
    if DEBUG:
        console.log(*obj)


def echo(msg, style: str = None, nl: bool = True):
    console.print(msg, style=style, end='\n' if nl else '')


def run(path, *args):
    path = os.path.join(APP, path)
    p = subprocess.Popen([path, *args])
    return p.wait()


@contextmanager
def pager(title=None):
    with console.capture() as cap:
        yield

    fd, path = tempfile.mkstemp()
    with open(path, 'w', encoding='utf-8') as f:
        f.write(cap.get())

    command = 'less -rf {} {}'.format(
        '--prompt=\'{}\''.format(title) if title else '',
        path
    )

    p = subprocess.Popen(command, shell=True)
    status = p.wait()

    os.close(fd)
    os.remove(path)


class Track(object):
    """
    track = Track(jobs, msg)

    """
    def __init__(self, jobs, msg='Working...', desc=''):
        self.progress = Progress(
            SpinnerColumn(),
            msg,
            TimeRemainingColumn(compact=True),
            BarColumn(),
            '[magenta]{task.percentage:>6.1f}%',
            '{task.description}',
            refresh_per_second = 20,
            console = console,
            transient = True
        )
        self.jobs = jobs
        self.task_id = self.progress.add_task(desc, total=len(jobs))
        

    def __iter__(self):
        with self.progress:
            for job in self.jobs:
                yield job
                self.progress.advance(self.task_id, advance=1)


    def update_desc(self, desc):
        self.progress.update(self.task_id, description=desc)


if __name__ == '__main__':
    import time
    a = Track(range(1,150))
    for i in a:
        time.sleep(0.1)
        a.desc(i)
