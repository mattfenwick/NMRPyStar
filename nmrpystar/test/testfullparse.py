from .. import fullparse
from ..unparse import maybeerror
from .. import ast as a
from ..ast import Data, Save, Loop
import unittest as u


parse = fullparse.parse
good = maybeerror.MaybeError.pure
bad = maybeerror.MaybeError.error


class TestFullParse(u.TestCase):
    
    def testParseGood(self):
        self.assertEqual(parse("data_hi save_me # oop \n   save_ "), 
                         good(Data('hi', {'me': Save({}, [])})))
    
    def testParseGoodComplex(self):
        inp = """
        data_start
         save_st1
          _a 1
          _b 2
         save_
         save_st2
          _c 3
          loop_
           _d _e
           w x y z m n
          stop_
         save_
        """
        ast = Data('start',
                   {'st1': Save({'a': '1', 'b': '2'}, []),
                    'st2': Save({'c': '3'}, [Loop(['d', 'e'], [['w', 'x'], ['y', 'z'], ['m', 'n']])])})
        self.assertEqual(parse(inp), good(ast))
    
    def testParseContextFreeProblem(self):
        self.assertEqual(parse("data_hi save_me # oop \n "), 
                         bad({'phase': 'CST construction', 
                              'message': [('data', (1,1)), ('save', (1,9)), ('save close', 'EOF')]}))
    
    def testParseContextSensitiveProblem(self):
        self.assertEqual(parse("data_hi save_me _a 1 _a 2 save_ "), 
                         bad({'phase': 'AST construction',
                              'message': {'message': 'duplicate key', 'nodetype': 'save',
                                          'key': 'a', 'first': (1,17), 'second': (1,22)}}))

    def testParseUnconsumedInput(self):
        self.assertEqual(parse("data_hi _what?"), 
                         bad({'phase': 'CST construction',
                              'message': [('unparsed tokens remaining', (1,9))]}))

    def testJunk(self):
        self.assertEqual(parse("what is this junk?  this isn't nmr-star"), 
                         bad({'phase': 'CST construction',
                              'message': [('data block', (1,1))]}))
