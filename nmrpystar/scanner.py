'''
@author: matt
'''
from .unparse.combinators import (many0,  optional,  app,   pure,  check,
                                  seq2R,  seq,       alt,   error,
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

identifier = node('identifier',
                  ('open', literal('_')),
                  ('value', cut('expected non-whitespace', many1(not1(space)))))

sc, sq, dq = map(literal, ';\'"')

_end = not0(item)
_not_space_or_end = not0(alt(space, _end))
nonEndingSq = seq2L(sq, _not_space_or_end)
nonEndingDq = seq2L(dq, _not_space_or_end)

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

_end_sc = seq(newline, sc)

def _sc_rest(position):
    _, column = position
    # a semicolon-delimited string must be preceded by a newline -- thus, column must be 1
    if column == 1:
        return node('scstring',
                    ('open', sc),
                    ('value', many0(not1(_end_sc))),
                    ('close', cut('newline-semicolon', _end_sc)))
    return zero
    
scstring = bind(getState, _sc_rest)

unquoted = node('unquoted',
                ('first', not1(special)),
                ('rest', many0(not1(space))))

token = alt(whitespace, 
            comment,
            sqstring,
            scstring, # I think it's important to put this before `unquoted` so that ; in column 1 will be an open-scstring
            dqstring,
            unquoted,
            identifier)

tokenizer = seq2L(many0(token),
                  cut('un-tokenizable input remaining', _end))
