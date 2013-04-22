
def parserFactory(Type):

    def result(value, rest, state):
        return {'result': value, 'rest': rest, 'state': state}

    def good(value, rest, state):
        return Type.pure(result(value, rest, state))

    class Parser(object):

        def __init__(self, parse):
            self.parse = parse

        def fmap(self, g):
            def h(r):
                return result(g(r['result']), r['rest'], r['state'])
            def f(xs, s):
                return self.parse(xs, s).fmap(h)
            return Parser(f)

        @staticmethod
        def pure(x):
            def f(xs, s):
                return good(x, xs, s)
            return Parser(f)

        def bind(self, g):
            def f(xs, s):
                r = self.parse(xs, s)
                val = r.value
                if r.status == 'success':
                    return g(val['result']).parse(val['rest'], val['state'])
                else:
                    return r
            return Parser(f)

        def plus(self, other):
            def f(xs, s):
                return self.parse(xs, s).plus(other.parse(xs, s))
            return Parser(f)

        @staticmethod
        def error(e):
            def f(xs, s):
                return Type.error(e)
            return Parser(f)

        def mapError(self, g):
            def f(xs, s):
                return self.parse(xs, s).mapError(g)
            return Parser(f)

        @staticmethod
        def put(xs):
            def f(_xs_, s):
                return good(None, xs, s)
            return Parser(f)

        @staticmethod
        def putState(s):
            def f(xs, _s_):
                return good(None, xs, s)
            return Parser(f)

        @staticmethod
        def updateState(g):
            def f(xs, s):
                return good(None, xs, g(s))
            return Parser(f)

        def check(self, p):
            def f(xs, s):
                r = self.parse(xs, s)
                if r.status != 'success':
                    return r
                elif p(r.value['result']):
                    return r
                return Type.zero
            return Parser(f)

        @staticmethod
        def literal(x):
            return Parser.item.check(lambda y: x == y)

        @staticmethod
        def satisfy(pred):
            return Parser.item.check(pred)

        def many0(self):
            def f(xs, s):
                vals = []
                tokens = xs
                state = s
                while True:
                    r = self.parse(tokens, state)
                    if r.status == 'success':
                        vals.append(r.value['result'])
                        state = r.value['state']
                        tokens = r.value['rest']
                    elif r.status == 'failure':
                        return good(vals, tokens, state)
                    else:  # must respect errors
                        return r
            return Parser(f)

        def many1(self):
            return self.many0().check(lambda x: len(x) > 0)

        @staticmethod
        def all(parsers):
            def f(xs, s):
                vals = []
                state, tokens = s, xs
                for p in parsers:
                    r = p.parse(tokens, state)
                    if r.status == 'error':
                        return r
                    elif r.status == 'success':
                        vals.append(r.value['result'])
                        state = r.value['state']
                        tokens = r.value['rest']
                    else:
                        return Type.zero
                return good(vals, tokens, state)
            return Parser(f)

        @staticmethod
        def app(f, *parsers):
            return Parser.all(parsers).fmap(lambda rs: f(*rs))

        def optional(self, x):
            return self.plus(Parser.pure(x))

        def seq2L(self, other):
            def f(x):
                return x[0]
            return Parser.all([self, other]).fmap(f)

        def seq2R(self, other):
            def g(x):
                return x[1]
            return Parser.all([self, other]).fmap(g)

        def not0(self):
            def f(xs, s):
                r = self.parse(xs, s)
                if r.status == 'error':
                    return r
                elif r.status == 'success':
                    return Type.zero
                else:
                    return good(None, xs, s)
            return Parser(f)

        def not1(self):
            return self.not0().seq2R(Parser.item)

        def commit(self, e):
            return self.plus(Parser.error(e))

        @staticmethod
        def string(elems):
            matcher = Parser.all(map(Parser.literal, elems))
            return matcher.seq2R(Parser.pure(elems))

        @staticmethod
        def any(parsers):
            def f(xs, s):
                r = Type.zero
                for p in parsers:
                    r = p.parse(xs, s)
                    if r.status in ['success', 'error']:
                        return r
                return r
            return Parser(f)


    Parser.zero = Parser(lambda xs, s: Type.zero)

    def f_item(xs, s):
        if xs.isEmpty():
            return Type.zero
        first, rest = xs.first(), xs.rest()
        return good(first, rest, s)

    Parser.item = Parser(f_item)

    def f_get(xs, s):
        return good(xs, xs, s)

    Parser.get = Parser(f_get)

    def f_getState(xs, s):
        return good(s, xs, s)

    Parser.getState = Parser(f_getState)


    return Parser
