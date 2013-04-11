from parse.standard import Parser
from nmrstar.tokens import Token


def lit(c):
    return Parser.satisfy(lambda t: t.char == c)

def str(cs):
    return Parser.all(map(lit, cs))

def extract(cs):
    return ''.join([x.char for x in cs])

def oneOf(cs):
    return Parser.satisfy(lambda x: x.char in cs)

NEWLINES = set('\n\r\f')
WHITESPACE = NEWLINES.union(set(' \t'))

_newline, _blank = map(oneOf, [NEWLINES, WHITESPACE])

stop = str("stop_").fmap(lambda xs: Token('stop', extract(xs), xs[0].meta))

saveclose = str("save_").fmap(lambda xs: Token('saveclose', extract(xs), xs[0].meta))

loop = str("loop_").fmap(lambda xs: Token('loop', extract(xs), xs[0].meta))


def commentAction(pd, chars):
    return Token('comment', extract(chars), pd.meta)
    
comment = Parser.app(commentAction, lit('#'), _newline.not1().many0())


def dataAction(open, name):
    return Token('dataopen', extract(name), open[0].meta)

dataopen = Parser.app(dataAction, str("data_"), _blank.not1().many1())
    
    
def saveAction(open, name):
    return Token('saveopen', extract(name), open[0].meta)

saveopen = Parser.app(saveAction, str("save_"), _blank.not1().many1())


def idAction(und, name):
    return Token('identifier', extract(name), und.meta)

identifier = Parser.app(idAction, lit('_'), _blank.not1().many1())


dq, esc_dq = lit('"'), lit('\\').seq2R(lit('"'))

def valueRest(open):
    def action(cs):
        return Token('value', extract(cs), open.meta)
    return (dq.not1()).plus(esc_dq).many1().fmap(action).seq2L(dq)

value = dq.bind(valueRest)


whitespace = _blank.many1().fmap(lambda xs: Token('whitespace', extract(xs), xs[0].meta))

token = Parser.any([dataopen, saveopen, saveclose,
                    loop, stop, value, whitespace,
                    comment, identifier])
                    
def noParse(ts):
    if ts.isEmpty():
        return Parser.zero
    else:
        return token.commit({'message': 'unable to parse token', 'position': ts.first().meta})
        
scanner = Parser.get.bind(noParse).many0()
