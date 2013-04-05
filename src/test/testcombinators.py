import parsercombinators.standard as s
import parsercombinators.maybeerror as me
import unittest as u


p = s.Parser
m = me.MaybeError


class TestParser(u.TestCase):
    
    def testPure(self):
        val = p.pure(3).parse('abc', 2)
        self.assertEqual(m.pure({'rest': 'abc', 'state': 2, 'result': 3}), val)
