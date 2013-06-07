

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

    def __repr__(self):
        return repr({'type': 'Token',
                     'tokentype': self.tokentype,
                     'value': self.value,
                     'meta': self.meta})

    def __eq__(self, other):
        try:
            return self.__dict__ == other.__dict__
        except:
            return False  # uhhh ... is this bad?
