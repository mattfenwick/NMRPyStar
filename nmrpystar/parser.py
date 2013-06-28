'''
@author: matt
'''
from .unparse import combinators as c
from . import concrete


item = c.itemPosition
(literal, satisfy, not1, _) = c.tokenPosition


extract = ''.join

def oneOf(cs):
    return satisfy(lambda x: x in cs)

def cut(message, parser):
    return c.bind(c.getState, 
                  lambda p: c.commit([(message, p)], parser))

def addError(e, parser):
    return c.bind(c.getState,
                  lambda pos: c.mapError(lambda es: [(e, pos)] + es, parser))
    

NEWLINES, BLANKS = set('\n\r'), set(' \t')
SPACES = NEWLINES.union(BLANKS)
SPECIALS = SPACES.union(set('"#\'_')) # double-quote, pound, single-quote, underscore

newline, blank, space, special = map(oneOf, [NEWLINES, BLANKS, SPACES, SPECIALS])

_identifier  =  c.app(lambda pos, _, bs: concrete.Key(pos, extract(bs)), 
                      c.getState, 
                      literal('_'), 
                      c.many1(not1(space)))


sc, sq, dq = map(literal, ';\'"')

end = c.not0(item)
_notSpaceOrEnd = c.not0(c.plus(space, end))
nonEndingSq = c.seq2L(sq, _notSpaceOrEnd)
nonEndingDq = c.seq2L(dq, _notSpaceOrEnd)

# empty        ->  fail
# not newline  ->  fail
# newline      ->  error
# (no success)
_newlineErr = addError('illegal newline', 
                       c.seq2R(newline, c.error([])))

sqstring = addError('single-quoted string',
                    c.app(lambda pos, _1, cs, _2: concrete.Value(pos, extract(cs)),
                          c.getState,
                          sq,
                          c.many0(c.plus(nonEndingSq, not1(c.plus(sq, _newlineErr)))),
                          cut("expected '", sq)))

dqstring = addError('double-quoted string',
                    c.app(lambda pos, _1, cs, _2: concrete.Value(pos, extract(cs)),
                          c.getState,
                          dq, 
                          c.many0(c.plus(nonEndingDq, not1(c.plus(dq, _newlineErr)))),
                          cut('expected "', dq)))

_quotedvalue = c.plus(sqstring, dqstring)


comment = c.app(lambda pos, _, b: concrete.Comment(pos, extract(b)), 
                c.getState,
                literal('#'),
                c.many0(not1(newline))) 

whitespace = c.app(concrete.Whitespace,
                   c.getState,
                   c.fmap(extract, c.many1(c.plus(blank, newline))))

junk = c.many0(c.plus(whitespace, comment))

endsc = c.seq2R(newline, sc)

def scRest(ws):
    _, column = ws
    # a semicolon-delimited string must be preceded by a newline -- thus, column must be 1
    if column == 1:
        return c.app(lambda pos, _1, b, _2: concrete.Value(pos, extract(b)),
                     c.getState,
                     sc,
                     c.many0(not1(endsc)),
                     cut('expected newline-semicolon', endsc))
    else:
        return c.zero
    
scstring = addError('semicolon string', 
                    c.bind(c.getState, scRest))

def classify(meta, theString): # 'theString' in order to avoid shadowing
    '''
    Classifications:
     - reserved: /stop_/, /loop_/, /save_.*/, /data_.+/
     - value:  everything else
    '''
    Reserved = concrete.Reserved
    if theString.lower() == "stop_":
        return Reserved(meta, "stop", None)
    elif theString[:5].lower() == "save_":
        if len(theString) != 5:
            return Reserved(meta, "saveopen", theString[5:])
        return Reserved(meta, "saveclose", None)
    elif theString.lower() == "loop_":
        return Reserved(meta, "loop", None)
    elif theString[:5].lower() == "data_" and len(theString) > 5:
        return Reserved(meta, "dataopen", theString[5:])
    return concrete.Value(meta, theString)

_uqvalue_or_keyword = c.app(lambda pos, c1, cs: classify(pos, extract([c1] + cs)),
                            c.getState,
                            not1(special),
                            c.many0(not1(space)))


def munch(parser):
    return c.seq2L(parser, junk)

uqvalue_or_keyword = munch(_uqvalue_or_keyword)

identifier  =  munch(_identifier)
value   =  c.check(lambda val: isinstance(val, concrete.Value), 
                   c.any_([munch(_quotedvalue), munch(scstring), uqvalue_or_keyword]))


# syntactic combinations
#   data blocks, save frames, loops, key/value pairs

def keyword(rtype):
    return c.check(lambda val: isinstance(val, concrete.Reserved) and val.rtype == rtype, 
                   uqvalue_or_keyword)

loop = addError('loop', 
                c.app(concrete.Loop,
                      keyword('loop'),
                      c.many0(identifier),
                      c.many0(value),
                      cut('expected "stop_"', keyword('stop'))))

datum = addError('datum',
                 c.app(concrete.Datum,
                       identifier, 
                       cut('expected value', value)))

save = addError('save',
                c.app(concrete.Save,
                      keyword('saveopen'),
                      c.many0(datum),
                      c.many0(loop),
                      cut('expected "save_"', keyword('saveclose'))))

data = addError('data', 
                c.app(concrete.Data,
                      keyword('dataopen'),
                      c.many0(save)))

end = c.not0(item)

nmrstar = c.app(lambda _1, d, _2: d,
                junk,
                cut('expected data block', data),
                cut('unparsed input remaining', end))
