import nmrstar.tokenizer as tfull
import nmrstar.simple.tokenizer as tsimple
import parse.position as p
import parse.conslist as c
import nmrstar.astparser as a



def tokenize(scanner, str):
    lcChars = c.ConsList.fromIterable(p.addLineCol(str))
    return scanner.parse(lcChars, None)

JUNKTYPES = set(['comment', 'whitespace', 'newlines'])
    
def stripJunk(tokens):
    return [t for t in tokens if t.tokentype not in JUNKTYPES]

def astParse(tokenization):
    stripped = stripJunk(tokenization['result'])
    return a.nmrstar.parse(c.ConsList.fromIterable(stripped), None)

def parse(scanner, input):
    tokens = tokenize(scanner, input)
    return tokens.bind(astParse)


def fullParse(input):
    return parse(tfull.scanner, input)

def simpleParse(input):
    return parse(tsimple.scanner, input)    