from tokenizer import scanner as tfull
from simple import scanner as tsimple
from parse import addLineCol, ConsList
from astparser import nmrstar
import parse.maybeerror as me



def tokenize(scanner, string):
    lcChars = ConsList.fromIterable(addLineCol(string))
    return scanner.parse(lcChars, None)


JUNKTYPES = set(['comment', 'whitespace', 'newlines'])

def stripJunk(tokens):
    return [t for t in tokens if t.tokentype not in JUNKTYPES]


def _sanityCheck(result):
    if not result['rest'].isEmpty():
        raise ValueError(('unexpected tokens remaining after parsing', result['rest']))
    return me.MaybeError.pure(result['result'])
    
def astParse(tokenization):
    # a sanity check -- tokenization should have consumed the entire input
    if not tokenization['rest'].isEmpty():
        raise ValueError(('unexpected input remaining after tokenization', tokenization['rest']))
    # cool, so we can ditch the 'rest' and 'state' fields
    stripped = stripJunk(tokenization['result'])
    parseResult = nmrstar.parse(ConsList.fromIterable(stripped), None)
    return parseResult.bind(_sanityCheck)


def parse(scanner, string):
    tokens = tokenize(scanner, string)
    return tokens.bind(astParse)


def fullParse(string):
    '''
    Parse string according to full NMR-Star
    syntactic definition.
    '''
    return parse(tfull, string)


def simpleParse(string):
    '''
    Parse string according to simplified NMR-Star
    syntactic definition.
    '''
    return parse(tsimple, string)
