from .scanner import tokenizer
from .cleantokens import clean_token
from .hierarchical import nmrstar
from .starast import concreteToAST
from .nmrstarast import build_nmrstar_ast
from .unparse.combinators import run
from .unparse.maybeerror import MaybeError


def _error(**kwargs):
    return MaybeError.error(kwargs)


_FIRST_TOKEN_INDEX = 0


def token_handler(string, status, value):
    if status == 'error':
        return _error(phase='tokenization', message=value)
    return _error(phase='tokenization', message='unexpected failure')


def parser_handler(cleaned, status, value):
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


def ast_handler(cst, status, value):
    if status == 'error':
        return _error(phase='AST construction', message=value)
    return _error(phase='AST construction', message='unexpected failure')


def nmrstar_handler(ast, status, value):
    if status == 'error':
        return _error(phase='NMRSTAR AST construction', message=value)
    return _error(phase='NMRSTAR AST construction', message='unexpected failure')


def parse_cst(string, f_token=token_handler, f_parser=parser_handler):
    '''
    Parse a string according to Star syntax.
    Result is a concrete syntax tree or an error,
    wrapped in a MaybeError container
     1. scanner
     2. ditch whitespace, comments
     3. clean up tokens
     4. CST
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
        return f_parser(cleaned, cst.status, cst.value)
    # sanity check
    tree = cst.value['result']
    if not cst.value['rest'].isEmpty():
        raise ValueError('unconsumed tokens remaining')
    return MaybeError.pure(tree)


def parse_star_ast(string, f_ast=ast_handler, **kwargs):
    '''
    Parse a string, constructing a STAR AST -- or an error,
    wrapped in a MaybeError container
     5. AST
    '''
    # part 5
    cst = parse_cst(string, **kwargs)
    if cst.status != 'success':
        return cst
    ast = concreteToAST(cst.value)
    if ast.status != 'success':
        return f_ast(cst, ast.status, ast.value)
    return ast
    

def parse_nmrstar_ast(string, f_nmrstar=nmrstar_handler, **kwargs):
    '''
    Parse a string, constructing an NMRSTAR AST -- or an error,
    wrapped in a MaybeError container
     6. NMRSTAR AST
    '''
    ast = parse_star_ast(string, **kwargs)
    if ast.status != 'success':
        return ast
    # part 6
    nmrstar_ast = build_nmrstar_ast(ast.value)
    if nmrstar_ast.status != 'success':
        return f_nmrstar(ast, nmrstar_ast.status, nmrstar_ast.value)
    # done
    return nmrstar_ast
