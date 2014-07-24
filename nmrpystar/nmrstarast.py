from . import starast
from .unparse.maybeerror import MaybeError
from collections import Counter


class Loop(starast.StarBase):

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


class Save(starast.StarBase):

    def __init__(self, prefix, category, datums, loops):
        if not isinstance(datums, dict):
            raise TypeError('saveframe datums must be a dict')
        if not isinstance(loops, dict):
            raise TypeError('saveframe loops must be a dict')
        self.prefix = prefix
        self.category = category
        self.datums = datums
        self.loops = loops

    def toJSONObject(self):
        loops = dict([(name, loop.toJSONObject()) for (name, loop) in self.loops.items()])
        return {'type'      : 'Save',
                'datums'    : self.datums,
                'prefix'    : self.prefix,
                'category'  : self.category,
                'loops'     : loops}


class Data(starast.StarBase):

    def __init__(self, name, saves):
        self.name = name
        if not isinstance(saves, dict):
            raise TypeError(('save frames must be a dict', saves, type(saves)))
        self.saves = saves

    def toJSONObject(self):
        return {'type'       : 'Data',
                'name'       : self.name,
                'save frames': dict((k, s.toJSONObject()) for (k, s) in self.saves.items())}


class ASTError(ValueError):

    def __init__(self, error):
        self.error = error

    def __repr__(self):
        return repr({'type': 'ASTError', 'error': self.error})
    
    def __str__(self):
        return repr(self)


def bad(**kwargs):
    raise ASTError(kwargs)


def parse_ident(string):
    """
    yes: 
        abc.def
        Assigned_chem_shift.ID
    no:
        abc
        .abc
        abc.
        .
    """
    dot_index = string.find('.')
    if dot_index == -1:
        bad(nodetype='identifier', message='missing prefix', key=string)
    elif dot_index == 0:
        bad(nodetype='identifier', message='invalid empty prefix', key=string)
    elif dot_index == len(string) - 1:
        bad(nodetype='identifier', message='invalid key postfix', key=string)
    return (string[:dot_index], string[dot_index+1:])


def build_loop(loop):
    '''
    ASTLoop -> (String, NMRSTAR-ASTLoop)
    0. 1+ keys
    1. consistent key prefix
    '''
    # 0. 1+ keys
    if len(loop.keys) == 0:
        bad(nodetype='loop', message='0 keys', loop=loop)

    prefixes, keys = set([]), []
    for node in loop.keys:
        pre, key = parse_ident(node)
        prefixes.add(pre)
        keys.append(key)
    
    # 1. consistent key prefix
    if len(prefixes) != 1:
        bad(nodetype='loop', message='inconsistent loop prefix',
            prefixes=prefixes)
    prefix = list(prefixes)[0]
    
    return (prefix, Loop(keys, loop.rows))
    

def build_save(name, save):
    '''
    0. 1+ keys
    1. consistent key prefixes
    2. presence of Sf_framecode and Sf_category keys
    3. matching of Sf_framecode value to save frame name
    4. duplicate loop prefixes
    '''
    loops, datums = {}, {}

    # 0.
    if len(save.datums) == 0:
        bad(nodetype='save', message='missing key/values', save=save)

    prefixes = set([])
    for (ident, value) in save.datums.items():
        pre, key = parse_ident(ident)
        prefixes.add(pre)
        datums[key] = value

    # 1.
    if len(set(prefixes)) != 1:
        bad(nodetype='save', message='inconsistent prefixes',
            prefixes=prefixes)
    prefix = list(prefixes)[0]

    # 2.
    for required_key in ['Sf_framecode', 'Sf_category']:
        # TODO what about Entry_ID and ID?
        if required_key not in datums:
            mess = 'missing key "%s"' % required_key
            bad(nodetype='save', message=mess)
    
    # 3.
    fcode = datums.pop('Sf_framecode')
    if fcode != name:
        bad(nodetype='save', expected=name, actual=fcode,
            message='Sf_framecode does not match save frame name')

    category = datums.pop('Sf_category')
    
    # 4.
    for my_loop in save.loops :
        (loop_prefix, loop) = build_loop(my_loop)
        if loop_prefix in loops:
            bad(nodetype='save', message='duplicate loop prefix',
                prefix=loop_prefix)
        loops[loop_prefix] = loop

    return Save(prefix, category, datums, loops)


def build_data(data):
    saves = {}
    for (name, my_save) in data.saves.items():
        save = build_save(name, my_save)
        saves[name] = save
    return Data(data.name, saves)
    

def build_nmrstar_ast(data):
    if not isinstance(data, starast.Data):
        raise TypeError(("expected starast.Data node", data))
    try:
        return MaybeError.pure(build_data(data))
    except ASTError, e:
        return MaybeError.error(e.error)
