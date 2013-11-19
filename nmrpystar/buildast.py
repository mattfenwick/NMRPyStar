'''
@author: matt
'''
from . import ast
from .unparse.maybeerror import MaybeError


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
        return good(ast.Loop(keys, []))

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

    return good(ast.Loop(keys, rows))
    

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

    return good(ast.Save(datums, loops))


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
    return good(ast.Data(dataName, mySaves))
    

def concreteToAST(node):
    if node['_name'] != 'data':
        raise TypeError(("expected concrete Data node", node))
    return buildData(node)
