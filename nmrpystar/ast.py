from .concrete import X


class Loop(X):

    def __init__(self, keys, rows):
        if not isinstance(keys, list):
            raise TypeError('Loop needs list of keys')
        if not isinstance(rows, list):
            raise TypeError('Loop neews list of rows')
        for r in rows:
            if not isinstance(r, list):
                raise TypeError('Loop rows must be lists')
        self.keys = keys
        self.rows = rows

    def toJSONObject(self):
        return {'type': 'Loop', 
                'keys': self.keys,
                'rows': self.rows}

    def getRowAsDict(self, rowIndex):
        return dict(zip(self.keys, self.rows[rowIndex]))


class Save(X):

    def __init__(self, datums, loops):
        if not isinstance(datums, dict):
            raise TypeError('saveframe datums must be a dict')
        if not isinstance(loops, list):
            raise TypeError('saveframe loops must be a list')
        self.datums = datums
        self.loops = loops

    def toJSONObject(self):
        return {'type'  : 'Save', 
                'datums': self.datums, 
                'loops' : [l.toJSONObject() for l in self.loops]}


class Data(X):

    def __init__(self, name, saves):
        self.name = name
        if not isinstance(saves, dict):
            raise TypeError(('save frames must be a dict', saves, type(saves)))
        self.saves = saves

    def toJSONObject(self):
        return {'type'       : 'Data', 
                'name'       : self.name, 
                'save frames': dict((k, s.toJSONObject()) for (k, s) in self.saves.items())}
