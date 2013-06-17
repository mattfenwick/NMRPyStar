'''
@author: matt
'''
from . import ast
from . import concrete
from .parse import maybeerror


MaybeError = maybeerror.MaybeError
good, bad = MaybeError.pure, MaybeError.error


def buildLoop(loop):
    pos, keys_1, vals_1 = loop.start, loop.keys, loop.values
    
    keys = [k.string for k in keys_1]
    vals = [v.string for v in vals_1]

    # duplicate keys
    key_check = set([])
    for key in keys:
        if key in key_check:
            return bad(('loop: duplicate key', key, pos))
        key_check.add(key)
            
    # no values
    if len(vals) == 0:
        return good(ast.Loop(keys, []))

    # values, but no keys -> throws ZeroDivisionError
    if len(vals) % len(keys) != 0:
        return bad(('loop: number of values must be integer multiple of number of keys', len(vals), len(keys), pos))
    
    rows, numKeys, valArr = [], len(keys), vals
    while len(valArr) > 0:
        rows.append(valArr[:numKeys])
        valArr = valArr[numKeys:]

    return good(ast.Loop(keys, rows))
    

def buildSave(save):
    ''' 
    list of loop/datum -> SaveFrame
    error conditions:
      - non-sequence (??? wtf does this mean ???)
      - non-loop/datum
      - duplicate datum keys
    '''
    vals = save.items
    loops, datums = [], {}

    for v in vals:
        if isinstance(v, concrete.Datum):
            key, value = v.key.string, v.value.string
            if datums.has_key(key):
                return bad(('save: duplicate key', key, save.start))
            datums[key] = value
        elif isinstance(v, concrete.Loop):
            l = buildLoop(v)
            if l.status == 'success':
                loops.append(l.value)
            else:
                return l
        else:
            raise TypeError(('save: invalid type', v))
    return good(ast.Save(datums, loops))


def buildData(node):
    dataName, saves = node.name, node.saves
    mySaves = {}
    for save in saves:
        if not isinstance(save, concrete.Save):
            raise TypeError(('Data expects Saves', save))
        if mySaves.has_key(save.name):
            return bad(('data: duplicate save frame name', save.name, node.start))
        s = buildSave(save)
        if s.status == 'success':
            mySaves[save.name] = s.value
        else:
            return s
    return good(ast.Data(dataName, mySaves))
    

def concreteToAST(node):
    if not isinstance(node, concrete.Data):
        raise TypeError(("expected concrete Data node", node))
    return buildData(node)
