

class Char(object):

    def __init__(self, char, meta):
        self.char = char
        self.meta = meta

    def __repr__(self):
        return repr(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def addLineCol(string):
    line, column, chars = 1, 1, []
    for x in string:
        chars.append(Char(x, {'line': line, 'column': column}))
        if x == '\n':
            line += 1
            column = 1
        else:
            column += 1
    return chars
