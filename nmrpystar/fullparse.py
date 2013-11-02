from .scanner import tokenizer
from .cleantokens import clean_token
from .parser import nmrstar
from .buildast import concreteToAST
from .unparse.combinators import run


def parse(string):
    '''
    Parse a string according to the full NMR-Star syntax.
    Result is an abstract syntax tree wrapped in a MaybeError container
    if successful, and an error message if not.
     1. scanner
     2. ditch whitespace, comments
     3. clean up tokens
     4. CST
     5. AST
    '''
    # part 1
    tokenized = run(tokenizer, string, (1, 1))
    if tokenized.status == 'failure': # sanity check
        raise ValueError('unexpected failure during tokenizing')
    if tokenized.status == 'error':
        return tokenized
    if not tokenized.value['rest'].isEmpty(): # sanity check
        raise ValueError('unconsumed characters remaining')
    # parts 2 and 3
    tokens = [clean_token(t) for t in tokenized.value['result'] if t['_name'] not in ['whitespace', 'comment']]
    # part 4
    cst = run(nmrstar, tokens, 1)
    if cst.status == 'failure': # sanity check
        raise ValueError('unexpected failure during parsing')
    if cst.status == 'error':
        return cst
    if not cst.value['rest'].isEmpty(): # sanity check
        raise ValueError('unconsumed tokens remaining')
    # part 5
    ast = concreteToAST(cst.value['result'])
    if ast.status == 'failure': # sanity check
        raise ValueError('unexpected failure during CST -> AST')
    return ast
