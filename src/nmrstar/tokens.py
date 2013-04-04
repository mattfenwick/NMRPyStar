
        
tokentypes = set(['dataopen', 'saveopen', 'saveclose', 'loop',
                  'stop', 'value', 'whitespace', 'newlines',
                  'comment', 'identifier'])

class Token(object):

    def __init__(self, ttype, value, meta):
        if ttype not in tokentypes:
            raise ValueError('bad token type: %s' % ttype)
        self.tokentype = ttype
        self.value = value
        self.meta = meta