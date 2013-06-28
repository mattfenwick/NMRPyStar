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

def run(p, i):
    return p.parse(i, (1, 1)) # assume state doesn't matter

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
            ["dAta_hello 123abc", 10, (1,11), concrete.Reserved(pos(1, 1), "dataopen", "hello"), 'data open'                      ],
            ["Save_bye oops",      8, (1, 9), concrete.Reserved(pos(1, 1), "saveopen", "bye")  , 'save open'                      ],
            ["saVE_ hi",           5, (1, 6), concrete.Reserved(pos(1, 1), "saveclose", None)  , 'save close'                     ],
            ["STOP_ matt",         5, (1, 6), concrete.Reserved(pos(1, 1), "stop", None)       , 'stop'                           ],
            ["loop_ us",           5, (1, 6), concrete.Reserved(pos(1, 1), "loop", None)       , 'loop open'                      ],
            ["LoOp_ hmm",          5, (1, 6), concrete.Reserved(pos(1, 1), "loop", None)       , 'keywords are case insensitive'  ],
            ["GLOBAl_ bye now",    7, (1, 8), concrete.Value(pos(1, 1), "GLOBAl_")             , 'global is not a keyword'        ],
            ["345 uh-oh",          3, (1, 4), concrete.Value(pos(1, 1), '345')                 , 'unquoted number'                ],
            ["abc def",            3, (1, 4), concrete.Value(pos(1, 1), 'abc')                 , 'unquoted alphas'                ],
            ['ab##_"123def\t???', 12, (1,13), concrete.Value(pos(1, 1), 'ab##_"123def')        , 'unquoted with special chars'    ],
            ["loop_uh-oh xx",     10, (1,11), concrete.Value(pos(1, 1), 'loop_uh-oh')          , 'unquoted can start with loop_'  ],
            ["stop_def 1",         8, (1, 9), concrete.Value(pos(1, 1), 'stop_def')            , 'unquoted can start with stop_'  ],
            ['global_"1 23blar',   9, (1,10), concrete.Value(pos(1, 1), 'global_"1')           , 'unquoted can start with global_'],
            ['data_   not',        5, (1, 6), concrete.Value(pos(1, 1), 'data_')               , 'data_ is a valid unquoted value']
        ]
        for (inp, num, pos2, v, message) in cases:
            print message
            output = good(l(inp[num:]), pos2, v)
            self.assertEqual(run(p.uqvalue_or_keyword, l(inp)), output)

    def testQuoteDelimitedValues(self):
        cases = [["'abc' 123",         5,  (1, 6),        'abc',                   'single-quoted string'],
                 ["'ab, c'd e' oh",   11,  (1,12),  "ab, c'd e",    'ending sq must be followed by space'],
                 ["'' qrs",            2,  (1, 3),           '',             'empty single-quoted string'],
                 ["'''",               3,  (1, 4),          "'",                        "sq in sq string"],
                 ["'ab''\n abc",       5,  (1, 6),        "ab'",  'ending sq can be followed by newlines'],
                 ['"abc" 123',         5,  (1, 6),        'abc',                   'double-quoted string'],
                 ['"ab, c"d e" oh',   11,  (1,12),  'ab, c"d e',    'ending dq must be followed by space'],
                 ['"" qrs',            2,  (1, 3),           '',             'empty double-quoted string'],
                 ['"""',               3,  (1, 4),          '"',                        "dq in dq string"],
                 ['"ab""\n abc',       5,  (1, 6),        'ab"',  'ending dq can be followed by newlines']]
        for (inp, num, pos2, value, message) in cases:
            output = good(l(inp[num:]), pos2, concrete.Value(pos(1, 1), value))
            print message
            self.assertEqual(run(p.value, l(inp)), output)
    
    def testValueLeadingSemicolon(self):
        cases = [
            ['\n;b\nr;x\n;..??', 9, (2, 1), (4,2), 'b\nr;x',                                        'semicolon string'],
            [' ;abc def',        5, (1, 2), (1,6), ';abc',      'semicolon not preceded by linebreak:  unquoted value'],
            [' \n;abc\n; def',   8, (2, 1), (3,2), 'abc',                                          ';-delimited value'],
            ['\n;\na;\n\n;def',  8, (2, 1), (5,2), '\na;\n',     ';-delimited value can contain ; but not linebreak-;'],
            ['\n;\n;def',        4, (2, 1), (3,2), '',                                                'empty ;-string'],
            [' ;abc o\nnt\n; d', 5, (1, 2), (1,6), ';abc',                                 'space-; -- unquoted value']]
        for (inp, num, pos1, pos2, value, message) in cases:
            output = good(l(inp[num:]), pos2, concrete.Value(pos(*pos1), value))
            print message
            self.assertEqual(run(p.value, l(inp)), output)
    
    def testIdentifier(self):
        inp = """_a"_#'$;3 \t\t"""
        output = good(l(inp[9:]), (1,10), concrete.Key(pos(1, 1), """a"_#'$;3"""))
        self.assertEqual(run(p.identifier, l(inp)), output)
    
    def testMunchBeforeToken(self):
        inp = '\t  # oo \n   # what \n \n\t \t_hithere'
        output = good(l([]), (4, 12), concrete.Key(pos(4, 4), "hithere"))
        self.assertEqual(run(p.identifier, l(inp)), output)
    
    
class TestTokenErrors(u.TestCase):
    
    def testDelimitedValueErrors(self):
        cases = [
            ["'abc 123"      , (1, 1),            'unclosed single-quoted string'],
            ['"abc 123'      , (1, 1),            'unclosed double-quoted string'],
            ["'abc \n ' de"  , (1, 1),  'illegal newline in single-quoted string'],
            ['"abc \n " de'  , (1, 1),  "illegal newline in double-quoted string"],
            ['\n;abc 123\na;', (2, 1),      'unclosed semicolon-delimited string']
        ]
        for (s, position, message) in cases:
            print message
            output = m.error((message, pos(*position)))
            self.assertEqual(run(p.value, l(s)), output)


class TestCombinations(u.TestCase):

    def testLoop(self):
        inp = '''
          loop_
            _a
            _bab
            1 2
            "wx" "yz"
          stop_'''
        output = good(l([]), None, concrete.Loop(pos(2, 11), 
                                                 [concrete.Key(pos(3, 13), 'a'),
                                                  concrete.Key(pos(4, 13), 'bab')],
                                                 [concrete.Value(pos(5, 13), '1'),
                                                  concrete.Value(pos(5, 15), '2'),
                                                  concrete.Value(pos(6, 13), 'wx'),
                                                  concrete.Value(pos(6, 18), 'yz')],
                                                 pos(7, 11)))
        self.assertEqual(run(p.loop, l(inp)), output)
        
    def testLoopMissingStop(self):
        inp = '''loop_ _a 1 2'''
        output = m.error(('loop: unable to parse', pos(1, 1)))
        self.assertEqual(run(p.loop, l(inp)), output)
        
    def testLoopInvalidContent(self):
        inp = 'loop_ _a _b 1 save_ stop_'
        output = m.error(('loop: unable to parse', pos(1, 1)))
        self.assertEqual(run(p.loop, l(inp)), output)
        
    def testDatum(self):
        inp = '_abc 123'
        output = good(l([]), None, concrete.Datum(concrete.Key(pos(1, 1), 'abc'), concrete.Value(pos(1, 6), '123')))
        self.assertEqual(run(p.datum, l(inp)), output)
    
    def testDatumMissingValue(self):
        inp = '_abc save_'
        output = m.error(('datum: missing value', pos(1, 1)))
        self.assertEqual(run(p.datum, l(inp)), output)
        
    def testSave(self):
        inp = 'save_me save_'
        output = good(l([]), None, concrete.Save(pos(1, 1), 'me', [], [], pos(1, 9)))
        self.assertEqual(run(p.save, l(inp)), output)
    
    def testSaveComplex(self):
        inp = ' save_thee _ab cd loop_ stop_ \nsave_ ' # <- a trailing space!
        output = good(l(inp[-1:]), None, concrete.Save(pos(1, 2), 
                                                 'thee',
                                                 [concrete.Datum(concrete.Key(pos(1, 12), 'ab'),
                                                                 concrete.Value(pos(1, 16), 'cd'))],
                                                 [concrete.Loop(pos(1, 19), [], [], pos(1, 25))],
                                                 pos(2, 1)))
        self.assertEqual(run(p.save, l(inp)), output)

    def testSaveUnclosed(self):
        inp = 'save_me _ab 12 '
        output = m.error(('save: unable to parse', pos(1, 1)))
        self.assertEqual(run(p.save, l(inp)), output)
        
    def testSaveInvalidContent(self):
        inp = '# hi\n save_me _ab 12 stop_ save_'
        output = m.error(('save: unable to parse', pos(2, 2)))
        self.assertEqual(run(p.save, l(inp)), output)
    
    def testSaveDatumAfterLoop(self):
        inp = "save_me _a b loop_ _x y stop_ \n _m n save_"
        output = m.error(('save: unable to parse', pos(1, 1)))
        self.assertEqual(run(p.save, l(inp)), output)
        
    def testData(self):
        inp = 'data_toks save_us save_ '
        output = good(l(inp[-1:]), None, concrete.Data(pos(1, 1), 
                                                       'toks',
                                                       [concrete.Save(pos(1, 11), 'us', [], [], pos(1, 19))]))
        self.assertEqual(run(p.data, l(inp)), output)
        
    def testDataInvalidContent(self):
        inp = 'data_me loop_ save_them save_'
        # it just hits the loop_, says, "I don't know how to deal with that",
        #   and doesn't consume it
        output = good(l(inp[7:]), None, concrete.Data(pos(1, 1), 'me', []))
        self.assertEqual(run(p.data, l(inp)), output)
        
    def testNMRStar(self):
        inp = 'data_me save_you \nsave_ # uh-oh??  '
        output = good(l([]), None, concrete.Data(pos(1, 1), 'me', [concrete.Save(pos(1, 9), 'you', [], [], pos(2, 1))]))
        self.assertEqual(run(p.nmrstar, l(inp)), output)
    
    def testNMRStarUnconsumedTokensRemaining(self):
        inp = 'data_me loop_ save_them save_'
        output = m.error(('unparsed input remaining', pos(1, 9)))
        self.assertEqual(run(p.nmrstar, l(inp)), output)
    
    def testNMRStarNoOpenData(self):
        inp = ' # save_me loop_ stop_ save_'
        output = m.error('unable to parse data block')
        self.assertEqual(run(p.nmrstar, l(inp)), output)
