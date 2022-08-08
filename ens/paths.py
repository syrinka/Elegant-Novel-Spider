from os.path import join, dirname


# 工作目录
CWD = dirname(dirname(__file__))

LOCAL = join(CWD, 'local')
DUMP = join(CWD, 'dump')

RES = join(CWD, 'ens', 'resources')

STATUS = join(RES, 'status.yml')
MANUAL = join(RES, 'man')

FLASK_PATH = join(RES, 'flask')
