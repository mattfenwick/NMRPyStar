'''
Created on Apr 22, 2013

@author: mattf
'''
from parse.standard import Parser


def _literal(c):
    return Parser.satisfy(lambda x: x.char == c)

def _string(cs):
    return Parser.all(map(_literal, cs))

_digs = dict(zip(map(str, range(10)), range(10)))  # {'0': 0, '1': 1, ...}

_digit = Parser.item.bind(lambda x: Parser.pure(_digs[x.char]) if x.char in _digs else Parser.zero)

_newline = Parser.satisfy(lambda x: x.char in '\n\r\f')

_space = Parser.satisfy(lambda x: x.char in ' \t')


line1 = _string('# Number of dimensions ').seq2R(_digit).seq2L(_newline)

def dimAction(_1, dimNumber, _2, dimName, _3):
    return (dimNumber, dimName)

dim = Parser.app(dimAction, _string('# INAME '), _digit, _space, Parser.item, _newline)

field = _newline.plus(_space).not1().many1()

def peakline(n):
    return Parser.app(lambda ident, shifts, _1: (ident, shifts), field, _space.many1().seq2R(Parser.all([field] * n)), _newline.not1().many0(), _newline)

xeasy = line1.bind(lambda n: dim.many1().seq2L(peakline(n).many0()))  # why many1 and many0 ??
