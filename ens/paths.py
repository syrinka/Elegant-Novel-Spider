from os.path import join, dirname


# 工作目录
CWD = dirname(dirname(__file__))
STATE = join(CWD, '.ens_state')
LOCAL = join(CWD, 'local')
DUMP = join(CWD, 'dump')
