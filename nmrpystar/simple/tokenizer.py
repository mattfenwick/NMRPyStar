from ..parse import Parser
from ..tokens import Token


def _literal(c):
    return Parser.satisfy(lambda t: t.char == c)

def _string(cs):
    return Parser.all(map(_literal, cs))

def _extract(cs):
    return ''.join([x.char for x in cs])

def _oneOf(cs):
    return Parser.satisfy(lambda x: x.char in cs)

_NEWLINES = set('\n\r\f')
_WHITESPACE = _NEWLINES.union(set(' \t'))

_newline, _blank = map(_oneOf, [_NEWLINES, _WHITESPACE])

stop = _string("stop_").fmap(lambda xs: Token('stop', _extract(xs), xs[0].meta))

saveclose = _string("save_").fmap(lambda xs: Token('saveclose', _extract(xs), xs[0].meta))

loop = _string("loop_").fmap(lambda xs: Token('loop', _extract(xs), xs[0].meta))


def _commentAction(pd, chars):
    return Token('comment', _extract(chars), pd.meta)

comment = Parser.app(_commentAction, _literal('#'), _newline.not1().many0())


def _dataAction(open_, name):
    return Token('dataopen', _extract(name), open_[0].meta)

dataopen = Parser.app(_dataAction, _string("data_"), _blank.not1().many1())


def _saveAction(open_, name):
    return Token('saveopen', _extract(name), open_[0].meta)

saveopen = Parser.app(_saveAction, _string("save_"), _blank.not1().many1())


def _idAction(und, name):
    return Token('identifier', _extract(name), und.meta)

identifier = Parser.app(_idAction, _literal('_'), _blank.not1().many1())


_dq = _literal('"')
_special = _oneOf(set('\\"'))
_simplechar = Parser.satisfy(lambda x: x.char not in set('\\"'))
_escape = _literal('\\').seq2R(_special)

def _valueRest(open_):
    def action(cs):
        return Token('value', _extract(cs), open_.meta)
    return (_simplechar).plus(_escape).many0().fmap(action).seq2L(_dq)

value = _dq.bind(_valueRest)


whitespace = _blank.many1().fmap(lambda xs: Token('whitespace', _extract(xs), xs[0].meta))

token = Parser.any([dataopen, saveopen, saveclose,
                    loop, stop, value, whitespace,
                    comment, identifier])

def noParse(ts):
    if ts.isEmpty():
        return Parser.zero
    else:
        return token.commit({'message': 'unable to parse token', 'position': ts.first().meta})

scanner = Parser.get.bind(noParse).many0()
