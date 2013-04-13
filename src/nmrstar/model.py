

class Loop(object):

    def __init__(self, keys, rows, meta):
        if not isinstance(keys, list):
            raise TypeError('Loop needs list of keys')
        if not isinstance(rows, list):
            raise TypeError('Loop neews list of rows')
        self.keys = keys
        self.rows = rows
        self.meta = meta
    
    @staticmethod
    def fromSimple(keys, vals, meta = None):
        # no values
        if len(vals) == 0:
            return Loop(keys, [], meta)

        # values, but no keys -> throws ZeroDivisionError
        if len(vals) % len(keys) != 0:
            raise ValueError(('number of values must be integer multiple of number of keys', len(vals), len(keys), meta))

        rows, numKeys, valArr = [], len(keys), vals
        while len(valArr) > 0:
            rows.append(valArr[:numKeys])
            valArr = valArr[numKeys:]

        return Loop(keys, rows, meta)
    
    def __repr__(self):
        return repr({'type': 'Loop', 'keys': self.keys, 
                     'rows': self.rows, 'meta': self.meta})
        
    def __eq__(self, other):
        # should 'meta' be included in the equality check?
        # should row order matter?
        return self.__dict__ == other.__dict__
    

class Save(object):

    def __init__(self, datums, loops, meta):
        if not isinstance(datums, dict):
            raise TypeError('saveframe datums must be a dict')
        if not isinstance(loops, list):
            raise TypeError('saveframe loops must be a list')
        self.datums = datums
        self.loops = loops
        self.meta = meta

    @staticmethod
    def fromSimple(vals, meta = None):
        ''' 
        list of loop/datum -> SaveFrame
        error conditions:
          - non-sequence
          - non-loop/datum
          - duplicate datum keys
        '''
        loops, datums = [], {}
        for v in vals:
            if isinstance(v, tuple):
                key, value = v
                if datums.has_key(key):
                    raise ValueError(('duplicate key', key))
                datums[key] = value
            elif isinstance(v, Loop):
                loops.append(v)
            else:
                raise TypeError(('invalid type', v))
        return Save(datums, loops, meta)
        
    def __repr__(self):
        return repr({'type': 'Save', 'datums': self.datums, 'loops': self.loops, 'meta': self.meta})
    
    def __eq__(self, other):
        # should 'meta' be included in the equality check?
        # should loop/datum order matter?
        return self.__dict__ == other.__dict__


class Data(object):

    def __init__(self, name, saves, meta):
        self.name = name
        if not isinstance(saves, dict):
            raise TypeError(('save frames must be a dict', saves, type(saves)))
        self.saves = saves
        self.meta = meta

    @staticmethod
    def fromSimple(dataName, saves, meta = None):
        mySaves = {}
        for (name, s) in saves:
            if not isinstance(s, Save):
                raise TypeError(('Data expects Saves', (name, s)))
            if mySaves.has_key(name):
                raise ValueError(('repeated save frame name', (name, s)))
            mySaves[name] = s
        return Data(dataName, mySaves, meta)
    
    def __repr__(self):
        return repr({'type': 'Data', 'name': self.name, 'save frames': self.saves, 'meta': self.meta})
        
    def __eq__(self, other):
        # should 'meta' be included in the equality check?
        # should save frame order matter?
        return self.__dict__ == other.__dict__


