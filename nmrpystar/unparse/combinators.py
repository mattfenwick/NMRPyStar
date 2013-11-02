from .maybeerror import MaybeError as M



class ConsList(object):
    '''
    A data structure that supports constant-time first/rest slicing.
    The input sequence is never copied or modified -- all the slicing
    does is increment a position counter and create a new wrapper.
    '''

    def __init__(self, seq, start=0):
        self.seq = seq
        self.start = start
        
    def isEmpty(self):
        return self.start >= len(self.seq)
        
    def first(self):
        '''
        Returns first element.  Throws exception if empty.
        '''
        if not self.isEmpty():
            return self.seq[self.start]
        raise ValueError('cannot get first element of empty sequence')
        
    def rest(self):
        '''
        Return ConsList of all but the first element.
        Throws exception if empty.
        '''
        if not self.isEmpty():
            return ConsList(self.seq, self.start + 1)
        raise ValueError('cannot get rest of empty sequence')
    
    def getAsList(self):
        '''
        Return list of remaining elements.
        '''
        return list(self.seq[self.start:])
        
    def __eq__(self, other):
        try:
            return self.getAsList() == other.getAsList()
        except:
            return False
    
    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __repr__(self):
        return repr({
            'type': 'cons list', 
            'sequence': self.getAsList()
        })



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

def seq(*parsers):
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
    return fmap(lambda rs: f(*rs), seq(*parsers))

def optional(parser, default=None):
    '''
    Parser e s (m t) a -> a -> Parser e s (m t) a
    '''
    return alt(parser, pure(default))

def _first(x, _):
    return x

def _second(_, y):
    return y

def seq2L(self, other):
    '''
    Parser e s (m t) a -> Parser e s (m t) b -> Parser e s (m t) a
    '''
    return app(_first, self, other)

def seq2R(self, other):
    '''
    Parser e s (m t) a -> Parser e s (m t) b -> Parser e s (m t) b
    '''
    return app(_second, self, other)

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
    return alt(parser, error(e))

def alt(*parsers):
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


class Itemizer(object):
    
    def __init__(self, item):
        '''
        item :: Parser e s (m t) t
        `item` is the most basic parser and should:
         - succeed, consuming one single token if there are any tokens left
         - fail if there are no tokens left
        '''
        self.item = item

    def literal(self, x):
        '''
        Eq t => t -> Parser e s (m t) t
        '''
        return check(lambda y: x == y, self.item)
    
    def satisfy(self, pred):
        '''
        (t -> Bool) -> Parser e s (m t) t
        '''
        return check(pred, self.item)
    
    def not1(self, parser):
        '''
        Parser e s (m t) a -> Parser e s (m t) t
        '''
        return seq2R(not0(parser), self.item)

    def string(self, elems):
        '''
        Eq t => [t] -> Parser e s (m t) [t] 
        '''
        matcher = seq(*map(self.literal, elems))
        return seq2R(matcher, pure(elems))
    
    def oneOf(self, elems):
        c_set = set(elems)
        return self.satisfy(lambda x: x in c_set)


def _f_item_basic(xs, s):
    '''
    Simply consumes a single token if one is available, presenting that token
    as the value.  Fails if token stream is empty.
    '''
    if xs.isEmpty():
        return M.zero
    first, rest = xs.first(), xs.rest()
    return good(first, rest, s)

basic = Itemizer(Parser(_f_item_basic))

def _bump(char, position):
    line, col = position
    if char == '\n':
        return (line + 1, 1)
    return (line, col + 1)

def _f_position(c):
    return seq2R(updateState(lambda s: _bump(c, s)), pure(c))

_item_position = bind(basic.item, _f_position)
position = Itemizer(_item_position)

_item_count = seq2L(basic.item, updateState(lambda x: x + 1))
count = Itemizer(_item_count)


def run(parser, input_string, state=(1,1)):
    '''
    Run a parser given the token input and state.
    '''
    return parser.parse(ConsList(input_string), state)
