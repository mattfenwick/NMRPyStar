'''
@author: matt
'''
from .unparse.combinators import (many0,  optional,  app,   pure,  check,
                                  seq2R,  Itemizer,  seq,   alt,   error,
                                  seq2L,  position,  not0,  many1, bind,
                                  zero,   getState)
from .unparse.cst import (node, sepBy0, cut, addError)


(item, literal, satisfy) = (position.item, position.literal, position.satisfy)
(oneOf, not1, string) = (position.oneOf, position.not1, position.string)


NEWLINES = '\n\r'
BLANKS   = ' \t'
SPACES   = '\n\r \t'
SPECIALS = '\n\r \t"#\'_' # double-quote, pound, single-quote, underscore

newline, blank, space, special = map(oneOf, [NEWLINES, BLANKS, SPACES, SPECIALS])

_identifier = node('identifier',
                   ('open', literal('_')),
                   ('value', cut('expected non-whitespace', many1(not1(space)))))

sc, sq, dq = map(literal, ';\'"')

end = not0(item)
_notSpaceOrEnd = not0(alt(space, end))
nonEndingSq = seq2L(sq, _notSpaceOrEnd)
nonEndingDq = seq2L(dq, _notSpaceOrEnd)

# empty        ->  fail
# not newline  ->  fail
# newline      ->  error
# (no success)
_newlineErr = addError('illegal newline', 
                       seq2R(newline, error([])))

sqstring = node('sqstring',
                ('open', sq),
                ('value', many0(alt(nonEndingSq, not1(alt(sq, _newlineErr))))),
                ('close', cut('single-quote', sq)))

dqstring = node('dqstring',
                ('open', dq),
                ('value', many0(alt(nonEndingDq, not1(alt(dq, _newlineErr))))),
                ('close', cut('double-quote', dq)))

comment = node('comment',
               ('open', literal('#')),
               ('value', many0(not1(newline))))

whitespace = node('whitespace',
                  ('value', many1(alt(blank, newline))))

junk = many0(alt(whitespace, comment))

endsc = seq2R(newline, sc)

def scRest(position):
    _, column = position
    # a semicolon-delimited string must be preceded by a newline -- thus, column must be 1
    if column == 1:
        return node('semicolon string',
                    ('open', sc),
                    ('value', many0(not1(endsc))),
                    ('close', cut('newline-semicolon', endsc)))
    return zero
    
scstring = bind(getState, scRest)

_loop_open = string('loop_')
_stop = string('stop_')
_save_open = node('save open',
                  ('open', string('save_')),
                  ('value', many0(not1(space))))
_save_close = string('save_')
_data_open = node('data open',
                  ('open', string('data_')),
                  ('value', many0(not1(space))))

_keyword = alt(_loop_open, _stop, _save_open, _save_close, _data_open)

_uq = node('uqvalue',
           ('first', not1(special)),
           ('rest', many0(not1(space))))

_uq_value = seq2R(not0(_keyword, _uq))

# syntactic combinations
#   data blocks, save frames, loops, key/value pairs

def munch(parser):
    return seq2L(parser, junk)

identifier  =  munch(_identifier)
value   =  munch(alt(sqstring, dqstring, scstring, _uq_value))

loop = node('loop',
            ('open', _loop_open),
            ('keys', many0(identifier)),
            ('values', many0(value)),
            ('close', cut("loop close", _stop)))

datum = node('datum',
             ('key', identifier),
             ('value', cut('value', value)))

save = node('save',
            ('open', _save_open),
            ('datums', many0(datum)),
            ('loops', many0(loop)),
            ('close', cut("save close", _save_close)))

data = node('data',
            ('open', _data_open),
            ('saveframes', many0(save)))

nmrstar = seq2R(junk,
                seq2L(cut('data block', data),
                      cut('unparsed input remaining', end))) # hmm, that error message is different from the others ....
