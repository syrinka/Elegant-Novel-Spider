from ens.paths import CONFIG
from pydantic import BaseSettings


class Config(BaseSettings):
    DEBUG: bool = False
    CODE_DELIM: str = '~'
    CODE_INDEX_INDICATOR: str = '#'
    EMPTY_RULE_MODE: str = '*='
    DEFAULT_DUMPER: str = 'txt'

    MERGE: str = 'smerge mergetool {old} {new} -o {new}'
    EDITOR: str = 'notepad {file}'

    class Config(object):
        env_file = CONFIG


config = Config()
