'''
@author: matt
'''
from . import ast
from .unparse.maybeerror import MaybeError


good, bad = MaybeError.pure, MaybeError.error


def buildLoop(loop):
    pos, keys_1, vals_1 = loop['_state'], loop['keys'], loop['values']
    
    keys = [k['value'] for k in keys_1]
    vals = [v['value'] for v in vals_1]

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
    if len(keys) == 0:
        return bad(('loop: keys but no values', pos))
    
    # number of values okay?
    if len(vals) % len(keys) != 0:
        return bad(('loop: number of values must be integer multiple of number of keys', 
                    len(vals), len(keys), pos))
    
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

    for d in save['datums']:
        key, value = d['key']['value'], d['value']['value']
        if datums.has_key(key):
            return bad(('save: duplicate key', key, save['_state']))
        datums[key] = value
    
    for loop in save['loops'] :
        l = buildLoop(loop)
        if l.status == 'success':
            loops.append(l.value)
        else:
            return l

    return good(ast.Save(datums, loops))


def buildData(node):
    dataName, saves = node['open']['value'], node['saves']
    mySaves = {}
    for save in saves:
        if save['_name'] != 'save': 
            raise TypeError(('Data expects Saves', save))
        if mySaves.has_key(save['open']['value']):
            return bad(('data: duplicate save frame name', save['open']['value'], node['_state']))
        s = buildSave(save)
        if s.status == 'success':
            mySaves[save['open']['value']] = s.value
        else:
            return s
    return good(ast.Data(dataName, mySaves))
    

def concreteToAST(node):
    if node['_name'] != 'data':
        raise TypeError(("expected concrete Data node", node))
    return buildData(node)
