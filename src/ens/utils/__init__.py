import yaml


def yaml_dump(obj):
    return yaml.dump(obj, allow_unicode=True, sort_keys=False)


def yaml_load(str):
    return yaml.load(str, Loader=yaml.SafeLoader)