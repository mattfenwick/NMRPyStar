from .. import parser as p
from .. import concrete
from .. import ast as md
from ..parse import position as np
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
        input = a("# abc\n123")
        output = good(l(input[5:]), None, concrete.Comment(pos(1, 1), " abc"))
        self.assertEqual(run(p.comment, l(input)), output)
    
    def testNewlines(self):
        for x in "\n\r\f":
            inp = a(x + "abc")
            output = good(l(inp[1:]), None, inp[0])
            self.assertEqual(run(p.newline, l(inp)), output)
    
    def testWhitespace(self):
        input = a(" \n \t \f\rabc")
        output = good(l(input[7:]), None, concrete.Whitespace(pos(1, 1), " \n \t \f\r"))
        self.assertEqual(run(p.whitespace, l(input)), output)

    def testUQValuesAndKeywords(self):
        cases = [
            ["data_hello 123abc", 10, concrete.Reserved(pos(1, 1), "dataopen", "hello")],
            ["save_bye oops",      8, concrete.Reserved(pos(1, 1), "saveopen", "bye")  ],
            ["save_ hi",           5, concrete.Reserved(pos(1, 1), "saveclose", '')    ],
            ["stop_ matt",         5, concrete.Reserved(pos(1, 1), "stop", '')         ],
            ["loop_ us",           5, concrete.Reserved(pos(1, 1), "loop", '')         ],
            ["345 uh-oh",          3, concrete.Value(pos(1, 1), '345')                 ],
            ["abc def",            3, concrete.Value(pos(1, 1), 'abc')                 ],
            ['ab##_"123def\t???', 12, concrete.Value(pos(1, 1), 'ab##_"123def')        ]
        ]
        for (s, num, v) in cases:
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
                 ['"ab""\n abc',           5,          'ab"',  'ending dq can be followed by newlines'],
                 [';abc\nqrs;xy\n;..???', 13,  'abc\nqrs;xy',                       'semicolon string']]
        for (s, num, value, message) in cases:
            inp = a(s)
            output = good(l(inp[num:]), None, concrete.Value(pos(1, 1), value))
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
    
    def testReservedErrors(self):
        cases = [
            "#\n data_ abc"      , # also tests the munching ... oops
            "# \n stop_abc"      ,
            "#hi  \n\tloop_oops"]
        for s in cases:
            output = m.error(('invalid keyword', pos(2, 2)))
            self.assertEqual(run(p.uqvalue_or_keyword, l(a(s))), output)
    
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
        output = good(l(inp[7:]), None, concrete.Data(pos(1, 1), 'me', []))
        self.assertEqual(run(p.data, l(inp)), output)
        
    def testNMRStar(self):
        pass
    
    def testNMRStarUnconsumedTokensRemaining(self):
        pass
    
hi = '''
    def testUnconsumedTokensRemaining(self):
        toks = l([dataopen, saveopen, ident, val, saveclose, val, dataopen])
        output = bad('unconsumed input remaining', dataopen)
        self.assertEqual(p.nmrstar.parse(toks, None), output)
'''