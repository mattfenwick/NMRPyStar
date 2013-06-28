from .. import parser as p
from .. import concrete
from .. import ast as md
from ..unparse import maybeerror as me
from ..unparse import conslist as c
import unittest as u


m = me.MaybeError
l = c.ConsList.fromIterable

def good(rest, state, result):
    return m.pure({'rest': rest, 'state': state, 'result': result})

def bad(message, position):
    return m.error({'message': message, 'position': position})

def run(parser, i, position = (1, 1)):
    return parser.parse(i, position)

def pos(line, column):
    return (line, column)



class TestTokenizer(u.TestCase):

    def testComment(self):
        inp = "# abc\n123"
        output = good(l(inp[5:]), (1,6), concrete.Comment(pos(1, 1), " abc"))
        self.assertEqual(run(p.comment, l(inp)), output)
    
    def testNewlines(self):
        out1 = good(l('abc'), (2, 1), '\n')
        self.assertEqual(run(p.newline, l('\nabc')), out1)
        out2 = good(l('abc'), (1, 2), '\r')
        self.assertEqual(run(p.newline, l('\rabc')), out2)
    
    def testWhitespace(self):
        inp = " \n \t \rabc"
        output = good(l(inp[6:]), (2,5), concrete.Whitespace(pos(1, 1), " \n \t \r"))
        self.assertEqual(run(p.whitespace, l(inp)), output)

    def testUQValuesAndKeywords(self):
        cases = [
            ["dAta_hello 123abc", 11, (1,12), concrete.Reserved(pos(1, 1), "dataopen", "hello"), 'data open'                      ],
            ["Save_bye oops",      9, (1,10), concrete.Reserved(pos(1, 1), "saveopen", "bye")  , 'save open'                      ],
            ["saVE_ hi",           6, (1, 7), concrete.Reserved(pos(1, 1), "saveclose", None)  , 'save close'                     ],
            ["STOP_ matt",         6, (1, 7), concrete.Reserved(pos(1, 1), "stop", None)       , 'stop'                           ],
            ["loop_ us",           6, (1, 7), concrete.Reserved(pos(1, 1), "loop", None)       , 'loop open'                      ],
            ["LoOp_ hmm",          6, (1, 7), concrete.Reserved(pos(1, 1), "loop", None)       , 'keywords are case insensitive'  ],
            ["GLOBAl_ bye now",    8, (1, 9), concrete.Value(pos(1, 1), "GLOBAl_")             , 'global is not a keyword'        ],
            ["345 uh-oh",          4, (1, 5), concrete.Value(pos(1, 1), '345')                 , 'unquoted number'                ],
            ["abc def",            4, (1, 5), concrete.Value(pos(1, 1), 'abc')                 , 'unquoted alphas'                ],
            ['ab##_"123def\t???', 13, (1,14), concrete.Value(pos(1, 1), 'ab##_"123def')        , 'unquoted with special chars'    ],
            ["loop_uh-oh xx",     11, (1,12), concrete.Value(pos(1, 1), 'loop_uh-oh')          , 'unquoted can start with loop_'  ],
            ["stop_def 1",         9, (1,10), concrete.Value(pos(1, 1), 'stop_def')            , 'unquoted can start with stop_'  ],
            ['global_"1 23blar',  10, (1,11), concrete.Value(pos(1, 1), 'global_"1')           , 'unquoted can start with global_'],
            ['data_   not',        8, (1, 9), concrete.Value(pos(1, 1), 'data_')               , 'data_ is a valid unquoted value']
        ]
        for (inp, num, pos2, v, message) in cases:
            print message
            output = good(l(inp[num:]), pos2, v)
            self.assertEqual(run(p.uqvalue_or_keyword, l(inp)), output)

    def testQuoteDelimitedValues(self):
        cases = [["'abc' 123",         6,  (1, 7),        'abc',                   'single-quoted string'],
                 ["'ab, c'd e' oh",   12,  (1,13),  "ab, c'd e",    'ending sq must be followed by space'],
                 ["'' qrs",            3,  (1, 4),           '',             'empty single-quoted string'],
                 ["'''",               3,  (1, 4),          "'",                        "sq in sq string"],
                 ["'ab''\n abc",       7,  (2, 2),        "ab'",  'ending sq can be followed by newlines'],
                 ['"abc" 123',         6,  (1, 7),        'abc',                   'double-quoted string'],
                 ['"ab, c"d e" oh',   12,  (1,13),  'ab, c"d e',    'ending dq must be followed by space'],
                 ['"" qrs',            3,  (1, 4),           '',             'empty double-quoted string'],
                 ['"""',               3,  (1, 4),          '"',                        "dq in dq string"],
                 ['"ab""\n abc',       7,  (2, 2),        'ab"',  'ending dq can be followed by newlines']]
        for (inp, num, pos2, value, message) in cases:
            output = good(l(inp[num:]), pos2, concrete.Value(pos(1, 1), value))
            print message
            self.assertEqual(run(p.value, l(inp)), output)
    
    def testValueLeadingSemicolon(self):
        cases = [
            [';b\nr;x\n;..??', 8, (1,1), (1, 1), (3,2), 'b\nr;x',                         'semicolon string'],
            [';abc def',       5, (1,2), (1, 2), (1,7), ';abc',      'not newline, then ; -- unquoted value'],
            [';abc\n; def',    7, (1,1), (1, 1), (2,3), 'abc',                           ';-delimited value'],
            [';\na;\n\n;def',  7, (1,1), (1, 1), (4,2), '\na;\n', ';-delimited can contain ; but not newline-;'],
            [';\n;def',        3, (1,1), (1, 1), (2,2), '',                                 'empty ;-string']]
        for (inp, num, pos0, pos1, pos2, value, message) in cases:
            output = good(l(inp[num:]), pos2, concrete.Value(pos(*pos1), value))
            print message
            self.assertEqual(run(p.value, l(inp), pos0), output)
    
    def testIdentifier(self):
        inp = """_a"_#'$;3 \t\tx"""
        output = good(l(inp[12:]), (1,13), concrete.Key(pos(1, 1), """a"_#'$;3"""))
        self.assertEqual(run(p.identifier, l(inp)), output)
    
    def testMunchAfterToken(self):
        inp = '_hithere\t  # oo \n   # what \n \n\t \t_hithere'
        output = good(l(inp[-8:]), (4, 4), concrete.Key(pos(1, 1), "hithere"))
        self.assertEqual(run(p.identifier, l(inp)), output)
    
    
class TestTokenErrors(u.TestCase):
    
    def testDelimitedValueErrors(self):
        cases = [
            ["'abc 123"      , [('single-quoted string', (1, 1)), ("expected '", (1, 9))]],
            ['"abc 123'      , [('double-quoted string', (1, 1)), ('expected "', (1, 9))]],
            ["'abc \n ' de"  , [('single-quoted string', (1, 1)), ('illegal newline', (1, 6))]],
            ['"abc \n " de'  , [('double-quoted string', (1, 1)), ('illegal newline', (1, 6))]],
            [';abc 123\na;'  , [('semicolon string',     (1, 1)), ('expected newline-semicolon', (2, 3))]]
        ]
        for (s, stack) in cases:
            print stack
            output = m.error(stack)
            self.assertEqual(run(p.value, l(s)), output)


class TestCombinations(u.TestCase):

    def testLoop(self):
        inp = '''loop_

            _a
            _bab
            1 2
            "wx" "yz"
          stop_'''
        output = good(l([]), (7, 16), concrete.Loop(concrete.Reserved(pos(1, 1), 'loop', None),
                                                    [concrete.Key(pos(3, 13), 'a'),
                                                     concrete.Key(pos(4, 13), 'bab')],
                                                    [concrete.Value(pos(5, 13), '1'),
                                                     concrete.Value(pos(5, 15), '2'),
                                                     concrete.Value(pos(6, 13), 'wx'),
                                                     concrete.Value(pos(6, 18), 'yz')],
                                                    concrete.Reserved(pos(7, 11), 'stop', None)))
        self.assertEqual(run(p.loop, l(inp)), output)
        
    def testLoopMissingStop(self):
        inp = 'loop_ _a 1 2'
        output = m.error([('loop', (1,1)), ('expected "stop_"', (1, 13))])
        self.assertEqual(run(p.loop, l(inp)), output)
        
    def testLoopInvalidContent(self):
        inp = 'loop_ \n  _a _b \n 1 \n save_ stop_'
        output = m.error([('loop', (1,1)), ('expected "stop_"', (4,2))])
        self.assertEqual(run(p.loop, l(inp)), output)
        
    def testDatum(self):
        inp = '_abc 123  \nt'
        output = good(l(inp[-1:]), (2,1), concrete.Datum(concrete.Key(pos(1, 1), 'abc'), 
                                                   concrete.Value(pos(1, 6), '123')))
        self.assertEqual(run(p.datum, l(inp)), output)
    
    def testDatumMissingValue(self):
        inp = '_abc save_'
        output = m.error([('datum', (1,1)), ('expected value', (1,6))])
        self.assertEqual(run(p.datum, l(inp)), output)
        
    def testSave(self):
        inp = 'save_me save_'
        output = good(l([]), (1,14), 
                      concrete.Save(concrete.Reserved((1, 1), 'saveopen', 'me'),
                                    [], 
                                    [], 
                                    concrete.Reserved((1, 9), 'saveclose', None)))
        self.assertEqual(run(p.save, l(inp)), output)
    
    def testSaveComplex(self):
        inp = 'save_thee  _ab cd loop_ stop_ \nsave_ t'
        output = good(l(inp[-1:]), (2,7), 
                      concrete.Save(concrete.Reserved((1, 1), 'saveopen', 'thee'), 
                                    [concrete.Datum(concrete.Key(pos(1, 12), 'ab'),
                                                    concrete.Value(pos(1, 16), 'cd'))],
                                    [concrete.Loop(concrete.Reserved((1, 19), 'loop', None), 
                                                   [], 
                                                   [], 
                                                   concrete.Reserved((1, 25), 'stop', None))],
                                    concrete.Reserved((2, 1), 'saveclose', None)))
        self.assertEqual(run(p.save, l(inp)), output)

    def testSaveUnclosed(self):
        inp = 'save_me _ab 12 '
        output = m.error([('save', (1, 1)), ('expected "save_"', (1, 16))])
        self.assertEqual(run(p.save, l(inp)), output)
        
    def testSaveInvalidContent(self):
        inp = 'save_me _ab \n12 stop_ save_'
        output = m.error([('save', (1,1)), ('expected "save_"', (2, 4))])
        self.assertEqual(run(p.save, l(inp)), output)
    
    def testSaveDatumAfterLoop(self):
        inp = "save_me \n_a b \nloop_ _x y stop_ \n _m n save_"
        output = m.error([('save', (1, 1)), ('expected "save_"', (4,2))])
        self.assertEqual(run(p.save, l(inp)), output)
        
    def testData(self):
        inp = 'data_toks save_us \nsave_ t'
        output = good(l(inp[-1:]), (2,7), 
                      concrete.Data(concrete.Reserved((1,1), 'dataopen', 'toks'),
                                    [concrete.Save(concrete.Reserved((1,11), 'saveopen', 'us'),
                                                   [], 
                                                   [], 
                                                   concrete.Reserved((2, 1), 'saveclose', None))]))
        self.assertEqual(run(p.data, l(inp)), output)
        
    def testDataInvalidContent(self):
        inp = 'data_me loop_ save_them save_'
        # it just hits the loop_, says, "I don't know how to deal with that",
        #   and doesn't consume it
        output = good(l(inp[8:]), (1,9), 
                      concrete.Data(concrete.Reserved((1, 1), 'dataopen', 'me'), 
                                    []))
        self.assertEqual(run(p.data, l(inp)), output)
        
    def testNMRStar(self):
        inp = ' data_me save_you \nsave_ # uh-oh?? \n '
        output = good(l([]), (3,2), 
                      concrete.Data(concrete.Reserved((1,2), 'dataopen', 'me'),
                                    [concrete.Save(concrete.Reserved((1, 10), 'saveopen', 'you'), 
                                                   [], 
                                                   [], 
                                                   concrete.Reserved((2, 1), 'saveclose', None))]))
        self.assertEqual(run(p.nmrstar, l(inp)), output)
    
    def testNMRStarUnconsumedTokensRemaining(self):
        inp = 'data_me loop_ save_them save_'
        output = m.error([('unparsed input remaining', pos(1, 9))])
        self.assertEqual(run(p.nmrstar, l(inp)), output)
    
    def testNMRStarNoOpenData(self):
        inp = '  save_me loop_ stop_ save_'
        output = m.error([('expected data block', (1, 3))])
        self.assertEqual(run(p.nmrstar, l(inp)), output)
