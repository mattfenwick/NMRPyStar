from .buildast import concreteToAST
from .parser import nmrstar
from .parse.conslist import ConsList
from .parse.position import addLineCol


def run(p, ts, s=None):
    '''
    just a temporary hack
    '''
    return p.parse(ConsList.fromIterable(addLineCol(ts)), s)


def cont(output):
    if not output['rest'].isEmpty(): # sanity check
        raise ValueError('successful parse must consume all input')
    return concreteToAST(output['result'])
        
def fullParse(string):
    conc = run(nmrstar, string)
    return conc.bind(cont)
    
__version__ = '0.0.11'