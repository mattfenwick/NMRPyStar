'''
@author: matt
'''


def token(my_type, position, **kwargs):
    kwargs['type'] = my_type
    kwargs['pos'] = position
    return kwargs

    
_simple = {'loop_': 'loop', 'stop_': 'stop', 'save_': 'save close'}

def classify(tok):
    val = ''.join([tok['first']] + tok['rest'])
    if val.lower() in _simple:
        return token('reserved', tok['_state'], keyword=_simple[val.lower()])
    elif val[:5].lower() == 'save_' and len(val) > 5:
        return token('reserved', tok['_state'], keyword='save open', value=val[5:])
    elif val[:5].lower() == 'data_' and len(val) > 5:
        return token('reserved', tok['_state'], keyword='data open', value=val[5:])
    return token('value', tok['_state'], value=val)

def string(tok):
    return token('value', tok['_state'], value=''.join(tok['value']))

def ident(tok):
    return token('identifier', tok['_state'], value=''.join(tok['value']))

actions = {
    'unquoted': classify,
    'identifier': ident,
    'sqstring': string,
    'dqstring': string,
    'scstring': string
}

def clean_token(token):
    name = token['_name']
    if name in actions:
        return actions[name](token)
    raise ValueError('invalid token name -- ' + name)
