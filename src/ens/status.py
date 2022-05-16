import yaml

from ens.paths import STATUS


class Status(object):
    _data = None

    def __init__(self, scope):
        self.scope = scope

        if self._data is None:
            try:
                # 将数据写入类中，确保所有实例访问的是相同的 status data
                self.__class__._data = yaml.load(
                    open(STATUS, encoding='utf-8'),
                    Loader = yaml.SafeLoader
                ) or dict()
            except FileNotFoundError:
                open(STATUS, 'w', encoding='utf-8') # create file
                self.__class__._data = dict()


    def _k(self, key):
        return self.scope + '.' + key


    def get(self, key, default=None):
        return self._data.get(self._k(key), default)


    def set(self, key, value):
        self._data[self._k(key)] = value
        return self


    def has(self, key):
        return self._k(key) in self._data


    def __getitem__(self, key):
        return self._data[self._k(key)]

    
    def __setitem__(self, key, value):
        self.set(key, value)


    def __delitem__(self, key):
        del self._data[self._k(key)]


    @classmethod
    def save(cls):
        yaml.dump(
            cls._data,
            open(STATUS, 'w', encoding='utf-8'),
            allow_unicode = True
        )


if __name__ == '__main__':
    status = Status('sys')
    
    status['a'] = 5
    print(status['a'])
    del status['a']
    status.save()
