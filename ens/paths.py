from os.path import join, dirname


# 工作目录
CWD = dirname(dirname(__file__))
STATE = join(CWD, '.ens_state')
CONFIG = join(CWD, 'ens_config')
LOCAL = join(CWD, 'local')
DUMP = join(CWD, 'dump')

RES = join(CWD, 'ens', 'resources')
MANUAL = join(RES, 'man')
FLASK_PATH = join(RES, 'flask')
