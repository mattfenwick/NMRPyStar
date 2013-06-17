from .. import fullparse
from ..parse import maybeerror
from .. import ast as a
import unittest as u


parse = fullparse.parse
good = maybeerror.MaybeError.pure
bad = maybeerror.MaybeError.error


class TestFullParse(u.TestCase):
    
    def testParseGood(self):
        self.assertEqual(parse("data_hi save_me # oop \n   save_ "), good(a.Data('hi', {'me': a.Save({}, [])})))
    
    def testParseContextFreeProblem(self):
        self.assertEqual(parse("data_hi save_me # oop \n "), bad(('save: unable to parse', {'line': 1, 'column': 9})))
    
    def testParseContextSensitiveProblem(self):
        self.assertEqual(parse("data_hi save_me _a 1 _a 2 save_ "), bad(('save: duplicate key', 
                                                                         'a', 
                                                                         {'line': 1, 'column': 9})))

    def testParseUnconsumedInput(self):
        self.assertEqual(parse("data_hi _what?"), bad(('unparsed input remaining', {'line': 1, 'column': 9})))
