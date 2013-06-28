from .. import fullparse
from ..unparse import maybeerror
from .. import ast as a
import unittest as u


parse = fullparse.parse
good = maybeerror.MaybeError.pure
bad = maybeerror.MaybeError.error

class TestFullParse(u.TestCase):
    
    def testParseGood(self):
        self.assertEqual(parse("data_hi save_me # oop \n   save_ "), 
                         good(a.Data('hi', {'me': a.Save({}, [])})))
    
    def testParseContextFreeProblem(self):
        self.assertEqual(parse("data_hi save_me # oop \n "), 
                         bad([('data', (1,1)), ('save', (1,9)), ('expected "save_"', (2,2))]))
    
    def testParseContextSensitiveProblem(self):
        self.assertEqual(parse("data_hi save_me _a 1 _a 2 save_ "), 
                         bad(('save: duplicate key', 
                              'a', 
                              (1, 9))))

    def testParseUnconsumedInput(self):
        self.assertEqual(parse("data_hi _what?"), 
                         bad([('unparsed input remaining', (1,9))]))

    def testJunk(self):
        self.assertEqual(parse("what is this junk?  this isn't nmr-star"), 
                         bad([('expected data block', (1,1))]))
