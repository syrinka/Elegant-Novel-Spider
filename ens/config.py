from pydantic import BaseSettings


class Config(BaseSettings):
    DEBUG: bool = False
    CODE_DELIM: str = '~'
    CODE_INDEX_INDICATOR: str = '#'
    EMPTY_RULE_MODE: str = '*='
    DEFAULT_DUMPER: str = 'txt'

    class Config(object):
        env_file = '.ens.config'


config = Config()
