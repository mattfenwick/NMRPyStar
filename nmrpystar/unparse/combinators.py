from .maybeerror import MaybeError as M



class Parser(object):
    '''
    A wrapper around a callable of type `[t] -> s -> ME ([t], s, a)`.
    Run the parser using the `parse` method.
    '''
    
    def __init__(self, parse):
        self.parse = parse
        

def result(value, rest, state):
    return {'result': value, 'rest': rest, 'state': state}

def good(value, rest, state):
    return M.pure(result(value, rest, state))

def compose(f, g):
    return lambda x: f(g(x))


def fmap(g, parser):
    '''
    (a -> b) -> Parser e s (m t) a -> Parser e s (m t) b
    '''
    def h(r):
        return result(g(r['result']), r['rest'], r['state'])
    def f(xs, s):
        return parser.parse(xs, s).fmap(h)
    return Parser(f)

def pure(x):
    '''
    a -> Parser e s (m t) a
    '''            
    def f(xs, s):
        return good(x, xs, s)
    return Parser(f)

def bind(parser, g):
    '''
    Parser e s (m t) a -> (a -> Parser e s (m t) b) -> Parser e s (m t) b
    '''
    def f(xs, s):
        r = parser.parse(xs, s)
        val = r.value
        if r.status == 'success':
            return g(val['result']).parse(val['rest'], val['state'])
        else:
            return r
    return Parser(f)

def plus(self, other):
    '''
    Parser e s (m t) a -> Parser e s (m t) a -> Parser e s (m t) a
    '''
    def f(xs, s):
        return self.parse(xs, s).plus(other.parse(xs, s))
    return Parser(f)

def error(e):
    '''
    e -> Parser e s (m t) a
    '''
    def f(xs, s):
        return M.error(e)
    return Parser(f)

def catchError(f, parser):
    '''
    Parser e s (m t) a -> (e -> Parser e s (m t) a) -> Parser e s (m t) a
    '''
    def g(xs, s):
        v = parser.parse(xs, s)
        if v.status == 'error':
            return f(v.value).parse(xs, s)
        return v
    return Parser(g)

def mapError(f, parser):
    '''
    Parser e s (m t) a -> (e -> e) -> Parser e s (m t) a
    '''
    return catchError(compose(error, f), parser)

def put(xs):
    '''
    m t -> Parser e s (m t) a
    '''
    def f(_xs_, s):
        return good(None, xs, s)
    return Parser(f)

def putState(s):
    '''
    s -> Parser e s (m t) a
    '''
    def f(xs, _s_):
        return good(None, xs, s)
    return Parser(f)

def updateState(g):
    '''
    (s -> s) -> Parser e s (m t) a
    '''
    def f(xs, s):
        return good(None, xs, g(s))
    return Parser(f)

def check(predicate, parser):
    '''
    (a -> Bool) -> Parser e s (m t) a -> Parser e s (m t) a
    '''
    def f(xs, s):
        r = parser.parse(xs, s)
        if r.status != 'success':
            return r
        elif predicate(r.value['result']):
            return r
        return M.zero
    return Parser(f)

def many0(parser):
    '''
    Parser e s (m t) a -> Parser e s (m t) [a]
    '''
    def f(xs, s):
        vals = []
        tokens = xs
        state = s
        while True:
            r = parser.parse(tokens, state)
            if r.status == 'success':
                vals.append(r.value['result'])
                state = r.value['state']
                tokens = r.value['rest']
            elif r.status == 'failure':
                return good(vals, tokens, state)
            else:  # must respect errors
                return r
    return Parser(f)

def many1(parser):
    '''
    Parser e s (m t) a -> Parser e s (m t) [a]
    '''
    return check(lambda x: len(x) > 0, many0(parser))

def all_(parsers):
    '''
    [Parser e s (m t) a] -> Parser e s (m t) [a]
    '''
    def f(xs, s):
        vals = []
        state, tokens = s, xs
        for p in parsers:
            r = p.parse(tokens, state)
            if r.status == 'success':
                vals.append(r.value['result'])
                state = r.value['state']
                tokens = r.value['rest']
            else:
                return r
        return good(vals, tokens, state)
    return Parser(f)

def app(f, *parsers):
    '''
    (a -> ... y -> z) -> Parser e s (m t) a -> ... -> Parser e s (m t) y -> Parser e s (m t) z
    '''
    return fmap(lambda rs: f(*rs), all_(parsers))

def optional(x, parser):
    '''
    Parser e s (m t) a -> a -> Parser e s (m t) a
    '''
    return plus(parser, pure(x))

def seq2L(self, other):
    '''
    Parser e s (m t) a -> Parser e s (m t) b -> Parser e s (m t) a
    '''
    def f(x):
        return x[0]
    return fmap(f, all_([self, other]))

def seq2R(self, other):
    '''
    Parser e s (m t) a -> Parser e s (m t) b -> Parser e s (m t) b
    '''
    def g(x):
        return x[1]
    return fmap(g, all_([self, other]))

def lookahead(parser):
    '''
    Parser e s (m t) a -> Parser e s (m t) None
    '''
    return bind(get, lambda xs: seq2R(parser, put(xs)))

def not0(parser):
    '''
    Parser e s (m t) a -> Parser e s (m t) None
    '''
    def f(xs, s):
        r = parser.parse(xs, s)
        if r.status == 'error':
            return r
        elif r.status == 'success':
            return M.zero
        else:
            return good(None, xs, s)
    return Parser(f)

def commit(e, parser):
    '''
    Parser e s (m t) a -> e -> Parser e s (m t) a
    '''
    return plus(parser, error(e))

def any_(parsers):
    '''
    [Parser e s (m t) a] -> Parser e s (m t) a
    '''
    def f(xs, s):
        r = M.zero
        for p in parsers:
            r = p.parse(xs, s)
            if r.status in ['success', 'error']:
                return r
        return r
    return Parser(f)

# Parser e s (m t) a
zero = Parser(lambda xs, s: M.zero)

# Parser e s (m t) (m t)
get = Parser(lambda xs, s: good(xs, xs, s))

# Parser e s (m t) s
getState = Parser(lambda xs, s: good(s, xs, s))


def tokenPrimitives(itemP):
    '''
    These parsers are built out of the most basic parser -- itemP -- that 
    consumes one single token if available.
    I couldn't figure out any better place to put them or thing to do with them --
    they don't seem to belong in a class, as far as I can tell.
    '''
    
    def literal(x):
        '''
        Eq t => t -> Parser e s (m t) t
        '''
        return check(lambda y: x == y, itemP)

    def satisfy(pred):
        '''
        (t -> Bool) -> Parser e s (m t) t
        '''
        return check(pred, itemP)

    def not1(self):
        '''
        Parser e s (m t) a -> Parser e s (m t) t
        '''
        return seq2R(not0(self), itemP)

    def string(elems):
        '''
        Eq t => [t] -> Parser e s (m t) [t] 
        '''
        matcher = all_(map(literal, elems))
        return seq2R(matcher, pure(elems))
    
    return (literal, satisfy, not1, string)


def _itemBasic(xs, s):
    '''
    Simply consumes a single token if one is available, presenting that token
    as the value.  Fails if token stream is empty.
    '''
    if xs.isEmpty():
        return M.zero
    first, rest = xs.first(), xs.rest()
    return good(first, rest, s)

itemBasic = Parser(_itemBasic)
tokenBasic = tokenPrimitives(itemBasic)


def _bump(c, p):
    line, col = p
    if c == '\n':
        return (line + 1, 1)
    return (line, col + 1)

def _itemPosition(xs, position):
    '''
    Does two things:
     - consumes a single token if available, failing otherwise (see `itemBasic`)
     - updates the position info in state -- `\n` is a newline
     
    This assumes that the state is a 2-tuple of integers, (line, column).
    '''
    if xs.isEmpty():
        return M.zero
    first, rest = xs.first(), xs.rest()
    return good(first, rest, _bump(first, position))

itemPosition = Parser(_itemPosition)
tokenPosition = tokenPrimitives(itemPosition)
