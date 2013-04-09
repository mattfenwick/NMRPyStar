

class Loop(object):

    def __init__(self, rows):
        if not isinstance(rows, list):
            raise TypeError('Loop needs list of rows')
        for r in rows:
            if not isinstance(r, dict):
                raise TypeError('Loop rows must be dictionaries')
        self.rows = rows
    
    @staticmethod
    def fromSimple(keys, vals):
        # no values
        if len(vals) == 0:
            return Loop([])

        # values, but no keys -> throws ZeroDivisionError
        if len(vals) % len(keys) != 0:
            raise ValueError('number of values must be integer multiple of number of keys')

        rows, numKeys, valArr = [], len(keys), vals
        while len(valArr) > 0:
            rows.append(dict(zip(keys, valArr[:numKeys])))
            valArr = valArr[numKeys:]

        return Loop(rows)
    
    def __repr__(self):
        return repr({'type': 'Loop', 'rows': self.rows})
    

class Save(object):

    def __init__(self, datums, loops):
        if not isinstance(datums, dict):
            raise TypeError('saveframe datums must be a dict')
        if not isinstance(loops, list):
            raise TypeError('saveframe loops must be a list')
        self.datums = datums
        self.loops = loops

    @staticmethod
    def fromSimple(vals):
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
        return Save(datums, loops)
        
    def __repr__(self):
        return repr({'type': 'Save', 'datums': self.datums, 'loops': self.loops})


class Data(object):

    def __init__(self, name, saves):
        self.name = name
        self.saves = saves

    @staticmethod
    def fromSimple(dataName, saves):
        mySaves = {}
        for (name, s) in saves:
            if not isinstance(s, Save):
                raise TypeError(('Data expects Saves', (name, s)))
            if mySaves.has_key(name):
                raise ValueError(('repeated save frame name', (name, s)))
            mySaves[name] = s
        return Data(dataName, mySaves)
    
    def __repr__(self):
        return repr({'type': 'Data', 'name': self.name, 'save frames': self.saves})


