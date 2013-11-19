from .scanner import tokenizer
from .cleantokens import clean_token
from .parser import nmrstar
from .buildast import concreteToAST
from .unparse.combinators import run
from .unparse.maybeerror import MaybeError


def _error(**kwargs):
    return MaybeError.error(kwargs)


_FIRST_TOKEN_INDEX = 0


def token_handler(string, status, value):
    if status == 'error':
        return _error(phase='tokenization', message=value)
    return _error(phase='tokenization', message='unexpected failure')


def parser_handler(string, tokens, cleaned, status, value):
    if status == 'error':
        err = []
        for (m, p) in value:
            if p - _FIRST_TOKEN_INDEX >= len(cleaned):
                err.append((m, 'EOF'))
            else:
                err.append((m, cleaned[p - _FIRST_TOKEN_INDEX]['pos']))
#        err = [(m, cleaned[p - 1]['pos']) for (m, p) in value]
        return _error(phase='CST construction', message=err)
    return _error(phase='CST construction', message='unexpected failure')


def ast_handler(string, tokens, cleaned, cst, status, value):
    if status == 'error':
        return _error(phase='AST construction', message=value)
    return _error(phase='AST construction', message='unexpected failure')


def parse(string, f_token=token_handler, f_parser=parser_handler, f_ast=ast_handler):
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
    if tokenized.status != 'success':
        return f_token(string, tokenized.status, tokenized.value)
    # sanity check
    if not tokenized.value['rest'].isEmpty():
        raise ValueError('unconsumed characters remaining')
    # part 2
    tokens = [t for t in tokenized.value['result'] if t['_name'] not in ['whitespace', 'comment']]
    # part 3
    cleaned = map(clean_token, tokens)
    # part 4
    cst = run(nmrstar, cleaned, _FIRST_TOKEN_INDEX)
    if cst.status != 'success':
        return f_parser(string, tokens, cleaned, cst.status, cst.value)
    # sanity check
    if not cst.value['rest'].isEmpty():
        raise ValueError('unconsumed tokens remaining')
    # part 5
    ast = concreteToAST(cst.value['result'])
    if ast.status != 'success':
        return f_ast(string, tokens, cleaned, cst, ast.status, ast.value)
    return ast
