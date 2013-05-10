'''
Created on Apr 22, 2013

@author: mattf
'''
from parse.standard import Parser
import xeasy.model as m


def _literal(c):
    return Parser.satisfy(lambda x: x.char == c)

def _string(cs):
    return Parser.all(map(_literal, cs))

def _oneOf(cs):
    chars = set(cs)
    return Parser.satisfy(lambda x: x.char in chars)

_dig         = _oneOf('0123456789').fmap(lambda x: x.char)
_digit       = _dig.fmap(int)
_int         = _dig.many1().fmap(lambda xs: ''.join(xs))
_integer     = _int.fmap(int)
_float       = Parser.app(lambda a, b, c: float(''.join([a, '.', c])), _int, _literal('.'), _int)

_newline     = _oneOf('\n\r\f')
_space       = _oneOf(' \t')


line1 = _string('# Number of dimensions ').seq2R(_digit).seq2L(_newline)


# the dim numbers are ignored; they're assumed
# to be the integers 1..n, in order and without
# any skipping
def dimAction(_1, _4, _2, dimName, _3):
    return dimName.char

dim = Parser.app(dimAction, _string('# INAME '), _digit, _space, Parser.item, _newline)

def dims(n):
    return Parser.all([dim] * n)


# what's the spec say about leading whitespace -- is it optional or required?
_ws_integer = _space.many0().seq2R(_integer)
_ws_float   = _space.many1().seq2R(_float)
_ws_field   = _space.many1().seq2R(_newline.plus(_space).not1().many1())

def peakline(n):
    return Parser.app(lambda ident, shifts, _fields1, height, _fields2, _newl: (ident, m.Peak(shifts, float(height))), 
                      _ws_integer,
                      Parser.all([_ws_float] * n).commit('a'),
                      Parser.all([_ws_field] * 2),
                      _ws_field.fmap(lambda x: ''.join([y.char for y in x])),
                      _ws_field.many0(), 
                      _newline)


def xeasyAction(dims, peaks):
    return m.PeakFile.fromSimple(dims, peaks)

def endCheck(p):
    def action(rest):
        if rest.isEmpty(): 
            return Parser.pure(None)
        return Parser.error({'message': 'unparsed input remaining', 'position': rest.first()})
    return p.seq2L(Parser.get.bind(action))

xeasy = endCheck(line1.bind(lambda n: Parser.app(xeasyAction, dims(n), peakline(n).many0())))
