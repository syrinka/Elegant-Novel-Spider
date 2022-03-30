import os
from os.path import join, dirname


def dn(path, layer=1):
    while layer:
        path = dirname(path)
        layer -= 1
    return path


CWD = dn(__file__, 3) # 工作目录

LOCAL = join(CWD, 'local')
DUMP = join(CWD, 'dump')

RES = join(CWD, 'src', 'resources')

APP = join(RES, 'app')
REMOTE_RES = join(RES, 'remote-res')
STATUS = join(RES, 'status.yml')
TOPIC = join(RES, 'topic')
MANUAL = join(RES, 'man')
