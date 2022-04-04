import yaml

from ens.paths import STATUS


class Status(object):
    _data = None

    def __init__(self, scope):
        self.scope = scope

        if self._data is None:
            # 将数据写入类中，确保所有实例访问的是相同的 status data
            self.__class__._data = yaml.load(
                open(STATUS, encoding='utf-8'),
                Loader = yaml.SafeLoader
            ) or dict()


    def _k(self, key):
        return self.scope + '.' + key


    def get(self, key, default):
        return self._data.get(self._k(key), default)


    def set(self, key, value):
        self._data[self._k(key)] = value


    def has(self, key):
        return self._k(key) in self._data


    def __getitem__(self, key):
        return self.get(key)

    
    def __setitem__(self, key, value):
        self.set(key, value)


    def __delitem__(self, key):
        del self._data[self._k(key)]


    def save(self):
        yaml.dump(
            self._data,
            open(STATUS, 'w', encoding='utf-8'),
            allow_unicode = True
        )


if __name__ == '__main__':
    status = Status('sys')
    
    status['a'] = 5
    print(status['a'])
    del status['a']
    status.save()
