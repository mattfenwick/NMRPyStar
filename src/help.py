def mapDict(f, d):
    return dict([(k, f(v)) for (k, v) in d.iteritems()])

def toJson(o):
    t = type(o)
    # lists, tuples, and sets
    if t in map(type, [[], (None,), set([])]):
        return map(toJson, o)
    # dictionaries
    if t == type({}):
        return mapDict(toJson, o)
    # instances of classes
    try:
        d = o.__dict__
        return mapDict(toJson, d)
    # everything else
    except AttributeError:
        return o
    # are any exceptions missed?
    
# what about:
#  - functions
#  - methods
#  - frozen sets
#  - classes
#  - modules
#  - ????
