
class X(object):
    '''
    Provides default:
     - equality
     - inequality
     - meaningful string representation 
    '''
    
    def __eq__(self, other):
        try:
            return self.__dict__ == other.__dict__
        except: # if the other object doesn't have a `__dict__` attribute, don't want to blow up 
            return False
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __repr__(self):
        return repr(self.toJSONObject())


class Data(X):
    
    def __init__(self, start, saves):
        self.start = start
        self.saves = saves
    
    def toJSONObject(self):
        return {'type' : 'data', 
                'start': self.start,
                'saves': [s.toJSONObject() for s in self.saves]}
    

class Save(X):
    
    def __init__(self, start, datums, loops, stop):
        self.start  =  start
        self.datums =  datums
        self.loops  =  loops
        self.stop   =  stop
    
    def toJSONObject(self):
        return {
            'type'  : 'save',
            'start' : self.start,
            'stop'  : self.stop,
            'datums': [d.toJSONObject() for d in self.datums],
            'loops' : [l.toJSONObject() for l in self.loops]
        }


class Loop(X):
    
    def __init__(self, start, keys, values, stop):
        self.start = start
        self.keys = keys
        self.values = values
        self.stop = stop
    
    def toJSONObject(self):
        return {'type'  : 'loop',
                'start' : self.start,
                'keys'  : [k.toJSONObject() for k in self.keys],
                'values': [v.toJSONObject() for v in self.values],
                'stop'  : self.stop}


class Datum(X):
    
    def __init__(self, key, value):
        self.key = key
        self.value = value
    
    def toJSONObject(self):
        return {'type' : 'datum',
                'key'  : self.key.toJSONObject(),
                'value': self.value.toJSONObject()}


class Key(X):
    
    def __init__(self, position, string):
        self.position = position
        self.string = string
    
    def toJSONObject(self):
        return {'type'  : 'key',
                'position' : self.position,
                'string': self.string}


class Value(X):
    
    def __init__(self, position, string):
        self.position = position
        self.string = string
    
    def toJSONObject(self):
        return {'type'  : 'value',
                'position' : self.position,
                'string': self.string}


_rtypes = set(['saveopen', 'dataopen', 'saveclose', 'stop', 'loop'])

class Reserved(X):
    
    def __init__(self, position, rtype, string):
        self.position = position
        if rtype not in _rtypes:
            raise ValueError(('invalid reserved keyword', rtype))
        self.rtype = rtype
        self.string = string
        
    def toJSONObject(self):
        return {'type'  : 'reserved',
                'position' : self.position,
                'rtype' : self.rtype,
                'string': self.string}


class Comment(X):
    
    def __init__(self, position, string):
        self.position = position
        self.string = string
    
    def toJSONObject(self):
        return {'type'  : 'comment',
                'position' : self.position,
                'string': self.string}


class Whitespace(X):
    
    def __init__(self, position, string):
        self.position = position
        self.string = string
    
    def toJSONObject(self):
        return {'type'  : 'whitespace',
                'position' : self.position,
                'string': self.string}
