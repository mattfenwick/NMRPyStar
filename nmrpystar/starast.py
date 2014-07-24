from .unparse.maybeerror import MaybeError


class StarBase(object):
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


class Loop(StarBase):

    def __init__(self, keys, rows):
        if not isinstance(keys, list):
            raise TypeError('Loop needs list of keys')
        if len(keys) != len(set(keys)):
            raise ValueError('Loop requires unique keys')
        if not isinstance(rows, list):
            raise TypeError('Loop needs list of rows')
        for r in rows:
            if not isinstance(r, list):
                raise TypeError('Loop rows must be lists')
            if len(r) != len(keys):
                raise ValueError('Loop row: %i keys, but %i values' % (len(keys), len(r)))
        self.keys = keys
        self.rows = rows

    def toJSONObject(self):
        return {'type': 'Loop', 
                'keys': self.keys,
                'rows': self.rows}

    def getRowAsDict(self, rowIndex):
        return dict(zip(self.keys, self.rows[rowIndex]))


class Save(StarBase):

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


class Data(StarBase):

    def __init__(self, name, saves):
        self.name = name
        if not isinstance(saves, dict):
            raise TypeError(('save frames must be a dict', saves, type(saves)))
        self.saves = saves

    def toJSONObject(self):
        return {'type'       : 'Data', 
                'name'       : self.name, 
                'save frames': dict((k, s.toJSONObject()) for (k, s) in self.saves.items())}



good = MaybeError.pure

def bad(**kwargs):
    return MaybeError.error(kwargs)


def buildLoop(loop):
    # duplicate keys
    key_check = {}
    for node in loop['keys']:
        key = node['value']
        if key in key_check:
            return bad(nodetype='loop', message='duplicate key', 
                       key=key, first=key_check[key]['pos'], second=node['pos'])
        key_check[key] = node

    # can't simply pull the keys out of `key_check` b/c that wouldn't preserve order
    keys = [k['value'] for k in loop['keys']]
    vals = [v['value'] for v in loop['values']]
    
    # no values
    if len(vals) == 0:
        return good(Loop(keys, []))

    # values, but no keys -> throws ZeroDivisionError
    if len(keys) == 0:
        return bad(nodetype='loop', message='values but no keys', position=loop['open']['pos'])
    
    # number of values okay?
    if len(vals) % len(keys) != 0:
        return bad(nodetype='loop', numkeys=len(keys), numvals=len(vals), position=loop['open']['pos'],
                   message='number of values must be integer multiple of number of keys')
    
    rows, numKeys, valArr = [], len(keys), vals
    while len(valArr) > 0:
        rows.append(valArr[:numKeys])
        valArr = valArr[numKeys:]

    return good(Loop(keys, rows))
    

def buildSave(save):
    ''' 
    error conditions:
      - non-loop/datum
      - duplicate datum keys
    '''
    loops, datums = [], {}
    key_check = {}

    for d in save['datums']:
        key, value = d['key']['value'], d['value']['value']
        if datums.has_key(key):
            return bad(nodetype='save', message='duplicate key',
                       key=key, first=key_check[key], second=d['key']['pos'])
        datums[key] = value
        key_check[key] = d['key']['pos']
    
    for loop in save['loops'] :
        l = buildLoop(loop)
        if l.status == 'success':
            loops.append(l.value)
        else:
            return l

    return good(Save(datums, loops))


def buildData(node):
    dataName, saves = node['open']['value'], node['saves']
    mySaves, save_check = {}, {}
    for save in saves:
        if save['_name'] != 'save': 
            raise TypeError(('Data expects Saves', save))
        name = save['open']['value']
        if name in save_check:
            return bad(nodetype='data', message='duplicate save frame name', 
                       name=name, first=save_check[name], second=save['open']['pos'])
        s = buildSave(save)
        if s.status == 'success':
            mySaves[save['open']['value']] = s.value
            save_check[name] = save['open']['pos']
        else:
            return s
    return good(Data(dataName, mySaves))
    

def concreteToAST(node):
    if node['_name'] != 'data':
        raise TypeError(("expected concrete Data node", node))
    return buildData(node)
