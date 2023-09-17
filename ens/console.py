import os
import subprocess
import tempfile
from contextlib import contextmanager
from typing import Iterable

import loguru
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TimeRemainingColumn
from rich.theme import Theme

from ens.config import config
from ens.exceptions import *

__all__ = [
    'logger',
    'console',
    'doing',
    'echo',
    'pager',
    'Track',
]

logger = loguru.logger

theme = Theme({
    'bad': 'red',
    'good': 'green',
    'alert': 'yellow',
    'fatal': 'red',
    'p': 'bright_white', # param
})
console = Console(highlight=False, theme=theme)
doing = console.status


def echo(*msg, style: str = None, nl: bool = True):
    console.print(*msg, style=style, end='\n' if nl else '')


@contextmanager
def pager(title=None):
    with console.capture() as cap:
        yield

    fd, path = tempfile.mkstemp()
    with open(path, 'w', encoding='utf-8') as f:
        f.write(cap.get())

    command = 'less -rf {} {}'.format(
        "--prompt='{}'".format(title) if title else '',
        path,
    )

    p = subprocess.Popen(command, shell=True)
    status = p.wait()

    os.close(fd)
    os.remove(path)


class Track(object):
    """
    track = Track(jobs, msg)

    """
    def __init__(self, jobs: Iterable, msg='Working...', desc=''):
        self.progress = Progress(
            SpinnerColumn(),
            msg,
            TimeRemainingColumn(compact=True, elapsed_when_finished=True),
            BarColumn(),
            '[magenta]{task.percentage:>6.1f}%',
            '{task.description}',
            refresh_per_second = 20,
            console = console,
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
        a.update_desc(i)
