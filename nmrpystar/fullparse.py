from .buildast import concreteToAST
from .parser import nmrstar
from .parse.conslist import ConsList
from .position import addLineCol


def run(p, ts, s=None):
    '''
    Parameters: parser, string-to-be-parsed, initial state
    Counts lines/columns of string, wraps in a ConsList,
    and runs parser over it, along with the supplied state.
    '''
    return p.parse(ConsList.fromIterable(addLineCol(ts)), s)


def concreteToAbstract(output):
    '''
    In:  concrete parse tree representing NMR-Star data
    Out:  abstract syntax tree representing NMR-Star data
    '''
    if not output['rest'].isEmpty(): # sanity check
        raise ValueError('successful parse must consume all input')
    return concreteToAST(output['result'])

        
def parse(string):
    '''
    Parse a string according to the full NMR-Star syntax.
    Result is an abstract syntax tree wrapped in a MaybeError container
    if successful, and an error message if not.
    '''
    conc = run(nmrstar, string)
    return conc.bind(concreteToAbstract)
