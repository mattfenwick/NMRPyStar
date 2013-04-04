from parser import Parser



# line and column, tokens, metadata

class Char(object):

    def __init__(self, char, meta):
        self.char = char
        self.meta = meta
        

def addLineCol(input):
    line, column, tokens = 1, 1, []
    for x in input:
        if x == '\n':
            line += 1
            column = 1
        tokens.append(Token(x, {'line': line, 'column': column}))
    return tokens



# hierarchical grammar

def tokentype(t):
    return Parser.satisfy(

Loop = loop.seq2R(Parser.all([

NMRStar