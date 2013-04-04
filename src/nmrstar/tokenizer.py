from parser import Parser
from tokens import Token


# token regexes
#
# newline = "^[\n\r\f]"
# blank = "^[ \t]"
# space = 

# tokens
#   needs error reporting
#   and take care of return values

def lit(c):
    return Parser.satisfy(lambda t: t.char == c)

def str(cs):
    return Parser.all(map(lit, cs))

def extract(cs):
    return [x.char for x in cs]


newline = Parser.any(map(lit, '\n\r\f'))

blank = lit(' ').plus(lit('\t'))

space = blank.plus(newline)

special = Parser.any(map(lit, '"#_')).plus(space)

stop = str("stop_")
    .fmap(lambda xs: Token('stop', extract(xs), xs[0].meta))

saveclose = str("save_")
    .fmap(lambda xs: Token('saveclose', extract(xs), xs[0].meta))

loop = str("loop_")
    .fmap(lambda xs: Token('loop', extract(xs), xs[0].meta))


def commentAction(pd, chars):
    return Token('comment', extract(chars), pd.meta)
    
comment = P.app(commentAction, lit('#'), newline.not1().many0())


def dataAction(open, name):
    return Token('dataopen', extract(name), open[0].meta)

dataopen = P.app(dataAction, str("data_"), space.not1().many1())
    
    
def saveAction(open, name):
    return Token('saveopen', [x.char for x in name], open[0].meta)

saveopen = P.app(saveAction, str("save_"), space.not1().many1())


def idAction(und, name):
    return Token('identifier', [x.char for x in name], und.meta)

identifier = P.app(idAction, lit('_'), space.not1().many1())

# stopped here
# the function is just cons
unquoted = Parser.app(lambda c, cs: [c] + cs, special.not1(), space.not1().many0())

sc, sq, dq = map(lit, ';\'"')

endsc = newline.seq2R(sc)

scstring = sc.seq2R(sc.not1().many0()).seq2L(sc)

sqstring = sq.seq2R(sq.not1().many1()).seq2L(sq)

dqstring = dq.seq2R(dq.not1().many1()).seq2L(dq)

value = Parser.any([sqstring, dqstring, scstring, unquoted])

whitespace = blank.many1()

newlines = newline.many1()

token = Parser.any([dataopen, saveopen, saveclose,
                    loop, stop, value, whitespace,
                    newlines, comment, identifier])