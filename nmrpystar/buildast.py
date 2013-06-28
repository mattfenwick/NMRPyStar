'''
@author: matt
'''
from . import ast
from . import concrete
from .unparse import maybeerror


MaybeError = maybeerror.MaybeError
good, bad = MaybeError.pure, MaybeError.error


def buildLoop(loop):
    pos, keys_1, vals_1 = loop.start.position, loop.keys, loop.values
    
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
    error conditions:
      - non-loop/datum
      - duplicate datum keys
    '''
    loops, datums = [], {}

    for d in save.datums:
        key, value = d.key.string, d.value.string
        if datums.has_key(key):
            return bad(('save: duplicate key', key, save.start.position))
        datums[key] = value
    
    for loop in save.loops:
        l = buildLoop(loop)
        if l.status == 'success':
            loops.append(l.value)
        else:
            return l

    return good(ast.Save(datums, loops))


def buildData(node):
    dataName, saves = node.start.string, node.saves
    mySaves = {}
    for save in saves:
        if not isinstance(save, concrete.Save):
            raise TypeError(('Data expects Saves', save))
        if mySaves.has_key(save.start.string):
            return bad(('data: duplicate save frame name', save.start.string, node.start.position))
        s = buildSave(save)
        if s.status == 'success':
            mySaves[save.start.string] = s.value
        else:
            return s
    return good(ast.Data(dataName, mySaves))
    

def concreteToAST(node):
    if not isinstance(node, concrete.Data):
        raise TypeError(("expected concrete Data node", node))
    return buildData(node)
