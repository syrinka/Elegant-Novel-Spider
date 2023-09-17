from typing import Optional

from pydantic import BaseSettings


class ENSConfig(BaseSettings):
    LOG_LEVEL: int = 0
    CODE_DELIM: str = '/'
    CODE_INDEX_INDICATOR: str = '@'
    EMPTY_RULE_MODE: str = '*='
    DEFAULT_DUMPER: str = 'txt'

    DO_EDIT: Optional[str] = None
    DO_MERGE: Optional[str] = None

    class Config(object):
        # .env is prior
        env_file = ('.env.example', '.env')


config = ENSConfig()
