import nmrstar.tokenizer as tfull
import nmrstar.simple.tokenizer as tsimple
import parse.position as p
import parse.conslist as c
import nmrstar.astparser as a



def tokenize(str):
    lcChars = c.ConsList.fromIterable(p.addLineCol(str))
    return t.scanner.parse(lcChars, None)
    

JUNKTYPES = set(['comment', 'whitespace', 'newlines'])
    
def stripJunk(tokens):
    return [t for t in tokens if t.tokentype not in JUNKTYPES]


def parse(input):
    tokens = tokenize(input)
    def astParse(tokenization):
        stripped = stripJunk(tokenization['result'])
        return a.nmrstar.parse(c.ConsList.fromIterable(stripped), None)
    return tokens.bind(astParse)
    