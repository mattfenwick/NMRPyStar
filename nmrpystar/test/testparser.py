from .. import parser as p
from .. import concrete
from .. import ast as md
from .. import position as np
from ..parse import maybeerror as me
from ..parse import conslist as c
from ..parse import standard
import unittest as u


Parser = standard.Parser
m = me.MaybeError
l = c.ConsList.fromIterable
a = np.addLineCol

def good(rest, state, result):
    return m.pure({'rest': rest, 'state': state, 'result': result})

def bad(message, position):
    return m.error({'message': message, 'position': position})

def run(p, i):
    return p.parse(i, None) # assume state doesn't matter

def pos(line, column):
    return {'line': line, 'column': column}



class TestTokenizer(u.TestCase):

    def testComment(self):
        inp = a("# abc\n123")
        output = good(l(inp[5:]), None, concrete.Comment(pos(1, 1), " abc"))
        self.assertEqual(run(p.comment, l(inp)), output)
    
    def testNewlines(self):
        for x in "\n\r\f":
            inp = a(x + "abc")
            output = good(l(inp[1:]), None, inp[0])
            self.assertEqual(run(p.newline, l(inp)), output)
    
    def testWhitespace(self):
        inp = a(" \n \t \f\rabc")
        output = good(l(inp[7:]), None, concrete.Whitespace(pos(1, 1), " \n \t \f\r"))
        self.assertEqual(run(p.whitespace, l(inp)), output)

    def testUQValuesAndKeywords(self):
        cases = [
            ["dAta_hello 123abc", 10, concrete.Reserved(pos(1, 1), "dataopen", "hello"), 'data open'                      ],
            ["Save_bye oops",      8, concrete.Reserved(pos(1, 1), "saveopen", "bye")  , 'save open'                      ],
            ["saVE_ hi",           5, concrete.Reserved(pos(1, 1), "saveclose", '')    , 'save close'                     ],
            ["STOP_ matt",         5, concrete.Reserved(pos(1, 1), "stop", '')         , 'stop'                           ],
            ["loop_ us",           5, concrete.Reserved(pos(1, 1), "loop", '')         , 'loop open'                      ],
            ["LoOp_ hmm",          5, concrete.Reserved(pos(1, 1), "loop", '')         , 'keywords are case insensitive'  ],
            ["GLOBAl_ bye now",    7, concrete.Reserved(pos(1, 1), "global", '')       , 'global'                         ],
            ["345 uh-oh",          3, concrete.Value(pos(1, 1), '345')                 , 'unquoted number'                ],
            ["abc def",            3, concrete.Value(pos(1, 1), 'abc')                 , 'unquoted alphas'                ],
            ['ab##_"123def\t???', 12, concrete.Value(pos(1, 1), 'ab##_"123def')        , 'unquoted with special chars'    ],
            ["loop_uh-oh xx",     10, concrete.Value(pos(1, 1), 'loop_uh-oh')          , 'unquoted can start with loop_'  ],
            ["stop_def 1",         8, concrete.Value(pos(1, 1), 'stop_def')            , 'unquoted can start with stop_'  ],
            ['global_"1 23blar',   9, concrete.Value(pos(1, 1), 'global_"1')           , 'unquoted can start with global_'],
            ['data_   not',        5, concrete.Value(pos(1, 1), 'data_')               , 'data_ is a valid unquoted value']
        ]
        for (s, num, v, message) in cases:
            print message
            inp = a(s)
            output = good(l(inp[num:]), None, v)
            self.assertEqual(run(p.uqvalue_or_keyword, l(inp)), output)

    def testValue(self):
        cases = [["'abc' 123",             5,          'abc',                   'single-quoted string'],
                 ["'ab, c'd e' oh",       11,    "ab, c'd e",    'ending sq must be followed by space'],
                 ["'' qrs",                2,             '',             'empty single-quoted string'],
                 ["'''",                   3,            "'",                        "sq in sq string"],
                 ["'ab''\n abc",           5,          "ab'",  'ending sq can be followed by newlines'],
                 ['"abc" 123',             5,          'abc',                   'double-quoted string'],
                 ['"ab, c"d e" oh',       11,    'ab, c"d e',    'ending dq must be followed by space'],
                 ['"" qrs',                2,             '',             'empty double-quoted string'],
                 ['"""',                   3,            '"',                        "dq in dq string"],
                 ['"ab""\n abc',           5,          'ab"',  'ending dq can be followed by newlines']]
        for (s, num, value, message) in cases:
            inp = a(s)
            output = good(l(inp[num:]), None, concrete.Value(pos(1, 1), value))
            print message
            self.assertEqual(run(p.value, l(inp)), output)
    
    def testValueLeadingSemicolon(self):
        cases = [
            ['\n;b\nr;x\n;..??', 9, (2, 1), 'b\nr;x',                                        'semicolon string'],
            [' ;abc def',        5, (1, 2), ';abc',      'semicolon not preceded by linebreak:  unquoted value'],
            [' \n;abc\n; def',   8, (2, 1), 'abc',    'linebreak-; , later on linebreak-; -- ;-delimited value'],
            ['\n;abc 123',       5, (2, 1), ';abc',    'linebreak-; , no linebreak-; later on:  unquoted value'],
            ['\n;\na;\n\n;def',  8, (2, 1), '\na;\n',     ';-delimited value can contain ; but not linebreak-;'],
            ['\n;\n;def',        4, (2, 1), '',      'empty ;-string'],
            [' ;abc o\nnt\n; d', 5, (1, 2), ';abc',  'space-; -- unquoted value']]
        for (s, num, myPosition, value, message) in cases:
            inp = a(s)
            output = good(l(inp[num:]), None, concrete.Value(pos(*myPosition), value))
            print message
            self.assertEqual(run(p.value, l(inp)), output)
    
    def testIdentifier(self):
        inp = a("""_a"_#'$;3 \t\t""")
        output = good(l(inp[9:]), None, concrete.Key(pos(1, 1), """a"_#'$;3"""))
        self.assertEqual(run(p.identifier, l(inp)), output)
    
    def testMunch(self):
        inp = a("  # hi \n \t #oops, a comment\n qrs")
        output = good(l(inp[-3:]), None, 'yes!')
        self.assertEqual(run(p.munch(Parser.pure('yes!')), l(inp)), output)
    
    def testMunchBeforeToken(self):
        inp = a('\t  # oo \n   # what \n \n\t \t_hithere')
        output = good(l([]), None, concrete.Key(pos(4, 4), "hithere"))
        self.assertEqual(run(p.identifier, l(inp)), output)
    
    
class TestTokenErrors(u.TestCase):
    
    def testDelimitedValueErrors(self):
        cases = [
            ['"abc 123',                'missing end double-quote'],
            ["'abc 123",                'missing end single-quote'],
            ["'abc \n ' de",'no newlines in single-quoted strings'],
            ['"abc \n " de',"no newlines in double-quoted strings"]
#            [";123\n hi\n", '']
        ]
        for (s, message) in cases:
            output = m.error((message, pos(1, 1)))
            self.assertEqual(run(p.value, l(a(s))), output)
                 
list_em = '''
    - unclosed double-quote string
    - unclosed single-quote string
    - unclosed ;-string
    - sq or dq string with newline in it
'''

class TestCombinations(u.TestCase):

    def testLoop(self):
        inp = a('''
          loop_
            _a
            _bab
            1 2
          stop_''')
        output = good(l([]), None, concrete.Loop(pos(2, 11), 
                                                 [concrete.Key(pos(3, 13), 'a'),
                                                  concrete.Key(pos(4, 13), 'bab')],
                                                 [concrete.Value(pos(5, 13), '1'),
                                                  concrete.Value(pos(5, 15), '2')],
                                                 pos(6, 11)))
        self.assertEqual(run(p.loop, l(inp)), output)
        
    def testLoopMissingStop(self):
        inp = a('''loop_ _a 1 2''')
        output = m.error(('loop: unable to parse', pos(1, 1)))
        self.assertEqual(run(p.loop, l(inp)), output)
        
    def testLoopInvalidContent(self):
        inp = a('loop_ _a _b 1 save_ stop_')
        output = m.error(('loop: unable to parse', pos(1, 1)))
        self.assertEqual(run(p.loop, l(inp)), output)
        
    def testDatum(self):
        inp = a('_abc 123')
        output = good(l([]), None, concrete.Datum(concrete.Key(pos(1, 1), 'abc'), concrete.Value(pos(1, 6), '123')))
        self.assertEqual(run(p.datum, l(inp)), output)
    
    def testDatumMissingValue(self):
        inp = a('_abc save_')
        output = m.error(('datum: missing value', pos(1, 1)))
        self.assertEqual(run(p.datum, l(inp)), output)
        
    def testSave(self):
        inp = a('save_me save_')
        output = good(l([]), None, concrete.Save(pos(1, 1), 'me', [], pos(1, 9)))
        self.assertEqual(run(p.save, l(inp)), output)
    
    def testSaveComplex(self):
        inp = a(' save_thee _ab cd loop_ stop_ \nsave_ ') # <- a trailing space!
        output = good(l(inp[-1:]), None, concrete.Save(pos(1, 2), 
                                                 'thee',
                                                 [concrete.Datum(concrete.Key(pos(1, 12), 'ab'),
                                                                 concrete.Value(pos(1, 16), 'cd')),
                                                  concrete.Loop(pos(1, 19), [], [], pos(1, 25))],
                                                 pos(2, 1)))
        self.assertEqual(run(p.save, l(inp)), output)

    def testSaveUnclosed(self):
        inp = a('save_me _ab 12 ')
        output = m.error(('save: unable to parse', pos(1, 1)))
        self.assertEqual(run(p.save, l(inp)), output)
        
    def testSaveInvalidContent(self):
        inp = a('# hi\n save_me _ab 12 stop_ save_')
        output = m.error(('save: unable to parse', pos(2, 2)))
        self.assertEqual(run(p.save, l(inp)), output)
        
    def testData(self):
        inp = a('data_toks save_us save_ ')
        output = good(l(inp[-1:]), None, concrete.Data(pos(1, 1), 
                                                       'toks',
                                                       [concrete.Save(pos(1, 11), 'us', [], pos(1, 19))]))
        self.assertEqual(run(p.data, l(inp)), output)
        
    def testDataInvalidContent(self):
        inp = a('data_me loop_ save_them save_')
        # it just hits the loop_, says, "I don't know how to deal with that",
        #   and doesn't consume it
        output = good(l(inp[7:]), None, concrete.Data(pos(1, 1), 'me', []))
        self.assertEqual(run(p.data, l(inp)), output)
        
    def testNMRStar(self):
        inp = a('data_me save_you \nsave_ # uh-oh??  ')
        output = good(l([]), None, concrete.Data(pos(1, 1), 'me', [concrete.Save(pos(1, 9), 'you', [], pos(2, 1))]))
        self.assertEqual(run(p.nmrstar, l(inp)), output)
    
    def testNMRStarUnconsumedTokensRemaining(self):
        inp = a('data_me loop_ save_them save_')
        output = m.error(('unparsed input remaining', pos(1, 9)))
        self.assertEqual(run(p.nmrstar, l(inp)), output)
