'''
@author: matt
'''
from . import ast
from . import concrete
from nmrpystar.parse.maybeerror import MaybeError



def buildLoop(keys_1, vals_1):
    keys = [k.string for k in keys_1]
    vals = [v.string for v in vals_1]

    # duplicate keys
    if len(keys) != len(set(keys)):
        raise ValueError("loop: duplicate keys")

    # no values
    if len(vals) == 0:
        return ast.Loop(keys, [])

    # values, but no keys -> throws ZeroDivisionError
    if len(vals) % len(keys) != 0:
        raise ValueError(('loop: number of values must be integer multiple of number of keys', len(vals), len(keys)))
    
    rows, numKeys, valArr = [], len(keys), vals
    while len(valArr) > 0:
        rows.append(valArr[:numKeys])
        valArr = valArr[numKeys:]

    return ast.Loop(keys, rows)
    

def buildSave(vals):
    ''' 
    list of loop/datum -> SaveFrame
    error conditions:
      - non-sequence (??? wtf does this mean ???)
      - non-loop/datum
      - duplicate datum keys
    '''
    loops, datums = [], {}
    for v in vals:
        if isinstance(v, concrete.Datum):
            key, value = v.key.string, v.value.string
            if datums.has_key(key):
                raise ValueError(('duplicate key', key))
            datums[key] = value
        elif isinstance(v, concrete.Loop):
            loops.append(buildLoop(v.keys, v.values))
        else:
            raise TypeError(('invalid type', v)) # this actually shouldn't happen
    return ast.Save(datums, loops)


def buildData(dataName, saves):
    mySaves = {}
    for save in saves:
        if not isinstance(save, concrete.Save):
            raise TypeError(('Data expects Saves', save)) # but ... this is an actual exception, it shouldn't happen
        if mySaves.has_key(save.name):
            raise ValueError(('repeated save frame name', save.name))
        mySaves[save.name] = buildSave(save.items)
    return ast.Data(dataName, mySaves)
    

def concreteToAST(node):
    if not isinstance(node, concrete.Data):
        raise TypeError(("expected concrete Data node", node)) # an actual exception
    try:
        return MaybeError.pure(buildData(node.name, node.saves))
    except Exception as e:
        return MaybeError.error(e)
    # when 'expected' errors are reported, the position information should be reported as well
