from parse import Parser
from tokens import Token


def _literal(c):
    return Parser.satisfy(lambda t: t.char == c)

def _string(cs):
    return Parser.all(map(_literal, cs))

def extract(cs):
    return ''.join([x.char for x in cs])

def oneOf(cs):
    return Parser.satisfy(lambda x: x.char in cs)

NEWLINES, BLANKS = set('\n\r\f'), set(' \t')
SPACES = NEWLINES.union(BLANKS)
SPECIALS = SPACES.union(set('"#_'))

newline, blank, space, special = map(oneOf, [NEWLINES, BLANKS, SPACES, SPECIALS])

stop = _string("stop_").fmap(lambda xs: Token('stop', extract(xs), xs[0].meta))

saveclose = _string("save_").fmap(lambda xs: Token('saveclose', extract(xs), xs[0].meta))

loop = _string("loop_").fmap(lambda xs: Token('loop', extract(xs), xs[0].meta))


def commentAction(pd, chars):
    return Token('comment', extract(chars), pd.meta)

comment = Parser.app(commentAction, _literal('#'), newline.not1().many0())


def dataAction(open_, name):
    return Token('dataopen', extract(name), open_[0].meta)

dataopen = Parser.app(dataAction, _string("data_"), space.not1().many1())


def saveAction(open_, name):
    return Token('saveopen', extract(name), open_[0].meta)

saveopen = Parser.app(saveAction, _string("save_"), space.not1().many1())


def idAction(und, name):
    return Token('identifier', extract(name), und.meta)

identifier = Parser.app(idAction, _literal('_'), space.not1().many1())


def uqAction(c, cs):
    return Token('value', extract([c] + cs), c.meta)

unquoted = Parser.app(uqAction, special.not1(), space.not1().many0())

sc, sq, dq = map(_literal, ';\'"')

endsc = newline.seq2R(sc)

def scAction(open_, body, close):
    return Token('value', extract(body), open_.meta)

scstring = Parser.app(scAction, sc, endsc.not1().many0(), endsc)

def sqRest(open_):
    def action(cs):
        return Token('value', extract(cs), open_.meta)
    nonEndingSq = sq.seq2L(space.not0())
    return nonEndingSq.plus(sq.not1()).many1().fmap(action).seq2L(sq)

sqstring = sq.bind(sqRest)

def dqRest(open_):
    def action(cs):
        return Token('value', extract(cs), open_.meta)
    return dq.not1().many1().fmap(action).seq2L(dq)

dqstring = dq.bind(dqRest)

value = Parser.any([sqstring, dqstring, scstring, unquoted])


whitespace = blank.many1().fmap(lambda xs: Token('whitespace', extract(xs), xs[0].meta))

newlines = newline.many1().fmap(lambda xs: Token('newlines', extract(xs), xs[0].meta))

token = Parser.any([dataopen, saveopen, saveclose,
                    loop, stop, value, whitespace,
                    newlines, comment, identifier])

def noParse(ts):
    if ts.isEmpty():
        return Parser.zero
    else:
        return token.commit({'message': 'unable to parse token', 'position': ts.first().meta})

scanner = Parser.get.bind(noParse).many0()
