import yaml


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
