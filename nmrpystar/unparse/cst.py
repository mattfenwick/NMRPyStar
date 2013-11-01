'''
@author: matt
'''
from .combinators import (bind, getState, commit, mapError,
                          app,  many0,    seq2R,  optional, 
                          seq, fmap)


def cut(message, parser):
    """
    assumes errors are lists
    """
    return bind(getState, lambda p: commit([(message, p)], parser))

def addError(e, parser):
    """
    assumes errors are lists, and
    that the state is a position
    """
    return bind(getState,
                lambda pos: mapError(lambda es: [(e, pos)] + es, parser))

# wish I could put `pairs` in a kwargs dictionary, but then the order would be lost
def node(name, *pairs):
    """
    1. runs parsers in sequence
    2. collects results into a dictionary
    3. grabs state at which parsers started
    4. adds an error frame
    """
    names = map(lambda x: x[0], pairs)
    if len(names) != len(set(names)):
        raise ValueError('duplicate names')
    if '_name' in names:
        raise ValueError('forbidden key: "_name"')
    if '_state' in names:
        raise ValueError('forbidden key: "_state"')
    def action(state, results):
        out = dict(results)
        out['_state'] = state
        out['_name'] = name
        return out
    def closure_workaround(s): # captures s
        return lambda y: (s, y)
    return addError(name, 
                    app(action, 
                        getState, 
                        seq(*[fmap(closure_workaround(s), p) for (s, p) in pairs])))


def _sep_action(fst, pairs):
    vals, seps = [fst], []
    for (sep, val) in pairs:
        vals.append(val)
        seps.append(sep)
    return {
        'values': vals, 
        'separators': seps
    }

def _pair(x, y):
    return (x, y)

def sepBy1(parser, separator):
    return app(_sep_action,
               parser,
               many0(app(_pair, separator, parser)))

def sepBy0(parser, separator):
    return optional(sepBy1(parser, separator), {'values': [], 'separators': []})
