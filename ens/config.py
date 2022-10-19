from typing import Optional

from ens.paths import CONFIG
from pydantic import BaseSettings


class Config(BaseSettings):
    LOG_LEVEL: int = 0
    CODE_DELIM: str = '~'
    CODE_INDEX_INDICATOR: str = '#'
    EMPTY_RULE_MODE: str = '*='
    DEFAULT_DUMPER: str = 'txt'

    DO_EDIT: Optional[str]
    DO_MERGE: Optional[str]

    class Config(object):
        env_file = CONFIG


config = Config()
