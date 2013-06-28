from .buildast import concreteToAST
from .parser import nmrstar
from .unparse.conslist import ConsList


def run(p, ts, s=(1, 1)):
    '''
    Parameters: parser, string-to-be-parsed, initial state
    Counts lines/columns of string, wraps in a ConsList,
    and runs parser over it, along with the supplied state.
    '''
    return p.parse(ConsList.fromIterable(ts), s)


def concreteToAbstract(output):
    '''
    In:  concrete parse tree representing NMR-Star data
    Out:  abstract syntax tree representing NMR-Star data
    '''
    if not output['rest'].isEmpty(): # sanity check -- this should not happen
        raise ValueError('successful parse must consume all input')
    return concreteToAST(output['result'])

        
def parse(string):
    '''
    Parse a string according to the full NMR-Star syntax.
    Result is an abstract syntax tree wrapped in a MaybeError container
    if successful, and an error message if not.
    '''
    concrete = run(nmrstar, string)
    if concrete.status == 'failure': # sanity check -- this should not happen
        raise ValueError('unexpected failure during parsing')
    abstract = concrete.bind(concreteToAbstract)
    if abstract.status == 'failure': # sanity check -- this should not happen
        raise ValueError('unexpected failure during concrete to abstract syntax tree conversion')
    return abstract
