import nmrstar.tokenizer as tfull
import nmrstar.simple.tokenizer as tsimple
import parse.position as p
import parse.conslist as c
import nmrstar.astparser as a



def tokenize(scanner, string):
    lcChars = c.ConsList.fromIterable(p.addLineCol(string))
    return scanner.parse(lcChars, None)


JUNKTYPES = set(['comment', 'whitespace', 'newlines'])

def stripJunk(tokens):
    return [t for t in tokens if t.tokentype not in JUNKTYPES]


def astParse(tokenization):
    stripped = stripJunk(tokenization['result'])
    return a.nmrstar.parse(c.ConsList.fromIterable(stripped), None)


def parse(scanner, string):
    tokens = tokenize(scanner, string)
    return tokens.bind(astParse)


def fullParse(string):
    '''
    Parse string according to full NMR-Star
    syntactic definition.
    '''
    return parse(tfull.scanner, string)


def simpleParse(string):
    '''
    Parse string according to simplified NMR-Star
    syntactic definition.
    '''
    return parse(tsimple.scanner, string)
