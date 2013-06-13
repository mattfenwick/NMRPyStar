'''
@author: matt
'''
from nmrpystar.parse.standard import Parser
from nmrpystar.parse.conslist import ConsList
from nmrpystar.parse.position import addLineCol
from . import concrete



def _literal(c):
    return Parser.satisfy(lambda t: t.char == c)

def _string(cs):
    return Parser.all(map(_literal, cs))

def extract(cs):
    '''
    Returns a string, containing all of the characters
      (without their meta information)
    '''
    return ''.join([x.char for x in cs])

def posFirst(cs):
    return cs[0].meta

def oneOf(cs):
    return Parser.satisfy(lambda x: x.char in cs)

NEWLINES, BLANKS = set('\n\r\f'), set(' \t')
SPACES = NEWLINES.union(BLANKS)
SPECIALS = SPACES.union(set('"#_'))

newline, blank, space, special = map(oneOf, [NEWLINES, BLANKS, SPACES, SPECIALS])

_identifier  =  Parser.app(concrete.Key, _literal('_').fmap(lambda c: c.meta), space.not1().many1().fmap(extract))


sc, sq, dq = map(_literal, ';\'"')
endsc = newline.seq2R(sc)
def scAction(op, body, _):
    return concrete.Value(op.meta, extract(body))

scstring = Parser.app(scAction, sc, endsc.not1().many0(), endsc)

nonEndingSq = sq.seq2L(space.not0())
def sqAction(op, body, _):
    return concrete.Value(op.meta, extract(body))

sqstring = Parser.app(sqAction, sq, nonEndingSq.plus(sq.not1()).many1(), sq)

dqstring = Parser.app(lambda o, b, _: concrete.Value(o.meta, extract(b)), dq, dq.not1().many1(), dq)

_value = Parser.any([sqstring, dqstring, scstring]) # unquoted taken care of by uq_or_keyword rule


comment = _literal('#').seq2R(newline.not1().many0())
whitespace = blank.plus(newline).many1()


def uqOrKey(c, cs):
    return (c.meta, extract([c] + cs))

def classify(v):
    '''
    Classifications:
     - reserved: /stop_/, /loop_/, /save_/, /save_.+/, /data_.+/
     - illegal:  /stop_.+/, /loop_.+/, /data_/
     - value:  everything else
    '''
    meta, string = v
    err, pure, Reserved = Parser.error, Parser.pure, concrete.Reserved
    if string[:5] == "stop_":
        if len(string) != 5:
            return err(('invalid keyword', string))
        return pure(Reserved(meta, "stop", ''))
    elif string[:5] == "save_":
        if len(string) != 5:
            return pure(Reserved(meta, "saveopen", string[5:]))
        return pure(Reserved(meta, "saveclose", ''))
    elif string[:5] == "loop_":
        if len(string) != 5:
            return err(('invalid keyword', string))
        return pure(Reserved(meta, "loop", ''))
    elif string[:5] == "data_":
        if len(string) == 5:
            return err(('invalid keyword', string))
        return pure(Reserved(meta, "dataopen", string[5:]))
    return pure(concrete.Value(meta, string))
        
_uqvalue_or_keyword = Parser.app(uqOrKey, special.not1(), space.not1().many0()).bind(classify)


def munch(p):
    return whitespace.plus(comment).many0().seq2R(p)

uqvalue_or_keyword = munch(_uqvalue_or_keyword)

identifier  =  munch(_identifier)
value       =  munch(_value).plus(uqvalue_or_keyword.check(lambda val: isinstance(val, concrete.Value)))


def keyword(rtype):
    return uqvalue_or_keyword.check(lambda val: isinstance(val, concrete.Reserved) and val.rtype == rtype)


loop = Parser.app(concrete.Loop, keyword('loop').fmap(lambda x: x.start), identifier.many0(), value.many0(), keyword('stop'))

datum = Parser.app(concrete.Datum, identifier, value)

save = Parser.app(lambda o, its, c: concrete.Save(o.start, o.string, its, c.start), keyword('saveopen'), loop.plus(datum).many0(), keyword('saveclose'))

data = Parser.app(lambda o, ss: concrete.Data(o.start, o.string, ss), keyword('dataopen'), save.many0())

def endCheck(xs):
    if xs.isEmpty():
        return Parser.pure(None)
    return Parser.error(('unparsed input remaining', xs.first().meta))

nmrstar = data.seq2L(munch(Parser.get.bind(endCheck)))


def run(p, ts, s=None):
    '''
    just a temporary hack
    '''
    return p.parse(ConsList.fromIterable(addLineCol(ts)), s)
