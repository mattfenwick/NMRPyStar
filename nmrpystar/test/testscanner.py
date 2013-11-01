'''
@author: matt
'''
from .. import scanner
from .. import ast as md
from ..unparse import maybeerror as me
from ..unparse import combinators
import unittest as u


m = me.MaybeError
l = combinators.ConsList
token = scanner.token

def good(rest, state, result):
    return m.pure({'rest': rest, 'state': state, 'result': result})

def run(parser, i, position = (1, 1)):
    return combinators.run(parser, i, position)

def node(name, pos, **kwargs):
    kwargs['_name'] = name
    kwargs['_state'] = pos
    return kwargs



class TestScanner(u.TestCase):

    def testComment(self):
        inp = "# abc\n123"
        output = good(l(inp[5:]), (1,6), 
                      node('comment', (1, 1), open='#', value=list(" abc")))
        self.assertEqual(run(token, inp), output)
    
    def testNewlines(self):
        out1 = good(l('abc'), (2, 1), node('whitespace', (1,1), value=['\n']))
        self.assertEqual(run(token, '\nabc'), out1)
        out2 = good(l('abc'), (1, 2), node('whitespace', (1,1), value=['\r']))
        self.assertEqual(run(token, '\rabc'), out2)
    
    def testWhitespace(self):
        inp = " \n \t \rabc"
        output = good(l(inp[6:]), (2,5), node('whitespace', (1, 1), value=list(" \n \t \r")))
        self.assertEqual(run(token, inp), output)

    def testUnquoted(self):
        cases = [
            ["dAta_hello 123abc", 10, 'data open'                 ],
            ["Save_bye oops",      8, 'save open'                 ],
            ["saVE_ hi",           5, 'save close'                ],
            ["STOP_ matt",         5, 'stop'                      ],
            ["loop_ us",           5, 'loop open'                 ],
            ["LoOp_ hmm",          5, 'keywords: case insensitive'],
            ["GLOBAl_ bye now",    7, 'uq: global_'               ],
            ["345 uh-oh",          3, 'uq: number'                ],
            ["abc def",            3, 'uq: alphas'                ],
            ['ab##_"123def\t???', 12, 'uq: special chars'         ],
            ["loop_uh-oh xx",     10, 'uq: start with loop_'      ],
            ["stop_def 1",         8, 'uq: start with stop_'      ],
            ['global_"1 23blar',   9, 'uq: start with global_'    ],
            ['data_   not',        5, 'uq: data_'                 ]
        ]
        for (inp, num, message) in cases:
            print message
            self.assertEqual(run(token, inp),
                             good(l(inp[num:]), (1, 1+num),
                                  node('unquoted', (1, 1), first=inp[0], rest=list(inp[1:num]))))

    def testSqString(self):
        cases = [["'abc' 123",         5,  (1, 6),        'abc',                   'single-quoted string'],
                 ["'ab, c'd e' oh",   11,  (1,12),  "ab, c'd e",    'ending sq must be followed by space'],
                 ["'' qrs",            2,  (1, 3),           '',             'empty single-quoted string'],
                 ["'''",               3,  (1, 4),          "'",                        "sq in sq string"],
                 ["'ab''\n abc",       5,  (1, 6),        "ab'",  'ending sq can be followed by newlines']]
        for (inp, num, pos2, value, message) in cases:
            output = good(l(inp[num:]), pos2, 
                          node('sqstring', (1,1), open="'", close="'", value=list(value)))
            print message
            self.assertEqual(run(token, inp), output)
    
    def testDqString(self):
        cases = [['"abc" 123',         5,  (1, 6),        'abc',                   'double-quoted string'],
                 ['"ab, c"d e" oh',   11,  (1,12),  'ab, c"d e',    'ending dq must be followed by space'],
                 ['"" qrs',            2,  (1, 3),           '',             'empty double-quoted string'],
                 ['"""',               3,  (1, 4),          '"',                        "dq in dq string"],
                 ['"ab""\n abc',       5,  (1, 6),        'ab"',  'ending dq can be followed by newlines']]
        for (inp, num, pos2, value, message) in cases:
            output = good(l(inp[num:]), pos2, 
                          node('dqstring', (1,1), open='"', close='"', value=list(value)))
            print message
            self.assertEqual(run(token, inp), output)
    
    def testScString(self):
        cases = [
            [';b\nr;x\n;..??', 8, (1,1), (1, 1), (3,2), 'b\nr;x', 'semicolon string'],
            [';abc\n; def',    6, (1,1), (1, 1), (2,2), 'abc',    ';-delimited value'],
            [';\na;\n\n;def',  7, (1,1), (1, 1), (4,2), '\na;\n', 'can contain ; but not newline-;'],
            [';\n;def',        3, (1,1), (1, 1), (2,2), '',       'empty ;-string']]
        for (inp, num, pos0, pos1, pos2, value, message) in cases:
            output = good(l(inp[num:]), pos2, 
                          node('scstring', pos1, value=list(value), open=';', close=list('\n;')))
            print message
            self.assertEqual(run(token, inp, pos0), output)
    
    def testUnquotedLeadingSemicolon(self):
        inp = ';abc def'
        self.assertEqual(run(token, inp, (1,2)),
                         good(l(' def'), (1,6),
                              node('unquoted', (1,2), first=';', rest=list('abc'))))    
    
    def testIdentifier(self):
        inp = """_a"_#'$;3 \t\tx"""
        output = good(l(inp[9:]), (1,10), 
                      node('identifier', (1,1), open='_', value=list("""a"_#'$;3""")))
        self.assertEqual(run(token, inp), output)
    
    
class TestErrors(u.TestCase):
    
    def testDelimitedValueErrors(self):
        cases = [
            ["'abc 123"      , [('sqstring', (1, 1)), ("single-quote", (1, 9))]],
            ['"abc 123'      , [('dqstring', (1, 1)), ('double-quote', (1, 9))]],
            ["'abc \n ' de"  , [('sqstring', (1, 1)), ('illegal newline', (1, 6))]],
            ['"abc \n " de'  , [('dqstring', (1, 1)), ('illegal newline', (1, 6))]],
            [';abc 123\na;'  , [('scstring', (1, 1)), ('newline-semicolon', (2, 3))]]
        ]
        for (s, stack) in cases:
            print stack
            output = m.error(stack)
            self.assertEqual(run(token, s), output)
    
    def testEmptyIdentifier(self):
        inp = '_ abc'
        output = m.error([('identifier', (1,1)), ('expected non-whitespace', (1,2))])
        self.assertEqual(run(token, inp), output)
