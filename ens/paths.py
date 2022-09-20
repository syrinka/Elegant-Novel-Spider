from os.path import join, dirname


# 工作目录
CWD = dirname(dirname(__file__))
STATE = join(CWD, '.ens.cache')
CONFIG = join(CWD, '.ens.config')
LOCAL = join(CWD, 'local')
DUMP = join(CWD, 'dump')

RES = join(CWD, 'ens', 'resources')
MANUAL = join(RES, 'man')
FLASK_PATH = join(RES, 'flask')
