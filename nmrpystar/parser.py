from tokenizer import scanner as tfull
from simple import scanner as tsimple
from parse import addLineCol, ConsList
from astparser import nmrstar



def tokenize(scanner, string):
    lcChars = ConsList.fromIterable(addLineCol(string))
    return scanner.parse(lcChars, None)


JUNKTYPES = set(['comment', 'whitespace', 'newlines'])

def stripJunk(tokens):
    return [t for t in tokens if t.tokentype not in JUNKTYPES]


def astParse(tokenization):
    stripped = stripJunk(tokenization['result'])
    return nmrstar.parse(ConsList.fromIterable(stripped), None)


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
