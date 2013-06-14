
class X(object):
    '''
    Provides default:
     - equality
     - inequality
     - meaningful string representation 
    '''
    
    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __repr__(self):
        return repr(self.toJSONObject())


class Data(X):
    
    def __init__(self, start, name, saves):
        self.start = start
        self.name = name
        self.saves = saves
    
    def toJSONObject(self):
        return {'type' : 'data', 
                'start': self.start,
                'name' : self.name, 
                'saves': [s.toJSONObject() for s in self.saves]}
    

class Save(X):
    
    def __init__(self, start, name, items, stop):
        self.start = start
        self.name = name
        self.items = items
        self.stop = stop
    
    def toJSONObject(self):
        return {'type' : 'save',
                'start': self.start,
                'stop' : self.stop,
                'name' : self.name,
                'items': [i.toJSONObject() for i in self.items]}


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
    
    def __init__(self, start, string):
        self.start = start
        self.string = string
    
    def toJSONObject(self):
        return {'type'  : 'key',
                'start' : self.start,
                'string': self.string}


class Value(X):
    
    def __init__(self, start, string):
        self.start = start
        self.string = string
    
    def toJSONObject(self):
        return {'type'  : 'value',
                'start' : self.start,
                'string': self.string}


_rtypes = set(['saveopen', 'dataopen', 'saveclose', 'stop', 'loop', 'global'])

class Reserved(X):
    
    def __init__(self, start, rtype, string):
        self.start = start
        if rtype not in _rtypes:
            raise ValueError(('invalid reserved keyword', rtype))
        self.rtype = rtype
        self.string = string
        
    def toJSONObject(self):
        return {'type'  : 'reserved',
                'start' : self.start,
                'rtype' : self.rtype,
                'string': self.string}


class Comment(X):
    
    def __init__(self, start, string):
        self.start = start
        self.string = string
    
    def toJSONObject(self):
        return {'type'  : 'comment',
                'start' : self.start,
                'string': self.string}


class Whitespace(X):
    
    def __init__(self, start, string):
        self.start = start
        self.string = string
    
    def toJSONObject(self):
        return {'type'  : 'whitespace',
                'start' : self.start,
                'string': self.string}
