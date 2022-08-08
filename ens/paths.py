from os.path import join, dirname


# 工作目录
CWD = dirname(dirname(__file__))
CACHE = join(CWD, '.ens.cache')
LOCAL = join(CWD, 'local')
DUMP = join(CWD, 'dump')

RES = join(CWD, 'ens', 'resources')
MANUAL = join(RES, 'man')
FLASK_PATH = join(RES, 'flask')
