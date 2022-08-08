import yaml
import subprocess
from typing import List, Dict


def flatten(catalog: List, index: Dict = None) -> str:
    piece = []
    for vol in catalog:
        piece.append(f'# {vol["name"]}')
        for cid in vol['cids']:
            if index is not None:
                piece.append(f'. {index.get(cid, "[新章节]")} ({cid})')
            else:
                piece.append(f'. {cid}')
    
    return '\n'.join(piece) + '\n'


def unflatten(s: str) -> List:
    catalog = []
    for i in s.split('\n'):
        if i.startswith('# '):
            catalog.append({
                'name': i[2:],
                'cids': []
            })
        elif i.startswith('. '):
            cid = i.rsplit('(', 1)[1][:-1]
            catalog[-1]['cids'].append(cid)
    return catalog


def call(args, quiet=False):
    return subprocess.call(
        args, 
        stdout=subprocess.DEVNULL if quiet else None
    )


def executable_exists(name):
    return call(['where', name], True) == 0


def yaml_dump(obj, path=None):
    """
    dump(obj) -> str
    dump(obj, path) -> None
    """
    if path is not None:
        file = open(path, 'w', encoding='utf-8')
        yaml.dump(obj, file, allow_unicode=True, sort_keys=False)
    else:
        return yaml.dump(obj, allow_unicode=True, sort_keys=False)


def yaml_load(str=None, *, path=None):
    """
    load(str) -> obj
    load(path=filepath) -> obj
    """
    if path is not None:
        file = open(path, 'r', encoding='utf-8')
        return yaml.load(file, Loader=yaml.SafeLoader)
    else:
        return yaml.load(str, Loader=yaml.SafeLoader)
