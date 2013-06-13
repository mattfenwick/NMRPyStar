from buildast import concreteToAST
from parser import nmrstar
from .parse.conslist import ConsList
from .parse.position import addLineCol


def run(p, ts, s=None):
    '''
    just a temporary hack
    '''
    return p.parse(ConsList.fromIterable(addLineCol(ts)), s)


__version__ = '0.0.10'