'''
@author: matt
'''
from .unparse.combinators  import (many0,  seq2L,  basic,  not0)
from .unparse.cst          import (node, cut)


(item, satisfy) = (basic.item, basic.satisfy)


def match(**kwargs):
    def test(t):
        for (k, v) in kwargs.items():
            if t[k] != v:
                return False
        return True
    return satisfy(test)

def reserved(my_type):
    return match(_name='reserved', type=my_type)

value = satisfy(lambda t: t['_name'] in ['scstring', 'sqstring', 'dqstring', 'unquoted value'])
ident = match(_name='identifier')

loop = node('loop',
            ('open'  , reserved('loop')),
            ('keys'  , many0(ident)),
            ('values', many0(value)),
            ('close' , cut("loop close", reserved('stop'))))

datum = node('datum',
             ('key'  , ident),
             ('value', cut('value', value)))

save = node('save',
            ('open'  , reserved('save open')),
            ('datums', many0(datum)),
            ('loops' , many0(loop)),
            ('close' , cut("save close", reserved('save close'))))

data = node('data',
            ('open'      , reserved('data open')),
            ('saveframes', many0(save)))

nmrstar = seq2L(cut('data block', data),
                cut('unparsed input remaining', not0(item))) # hmm, that error message is different from the others ....
