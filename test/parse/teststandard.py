import nmrpystar.parse.standard as s
import nmrpystar.parse.conslist as c
import nmrpystar.parse.maybeerror as me
import unittest as u


p = s.Parser
m = me.MaybeError

l = c.ConsList.fromIterable

def good(rest, state, result):
    return m.pure({'rest': rest, 'state': state, 'result': result})


class TestParser(u.TestCase):
    
    def testPure(self):
        val = p.pure(3).parse('abc', 2)
        self.assertEqual(good('abc', 2, 3), val)
        
    def testPlus(self):
        g1, g2, b, e = p.pure(3), p.pure('hi'), p.zero, p.error('oops')
        self.assertEqual(g1.plus(g2).parse('abc', None), g1.parse('abc', None))
        self.assertEqual(b.plus(g2).parse('abc', 3), g2.parse('abc', 3))
        self.assertEqual(e.plus(g1).parse('abc', 4), e.parse('abc', 4))
    
    def testBind(self):
        two = p.item.bind(lambda x: p.literal(x))
        self.assertEqual(two.parse(l('abcde'), {}), m.zero)
        self.assertEqual(two.parse(l('aabcde'), {}), good(l('bcde'), {}, 'a'))

    def testPut(self):
        val = p.put('xyz')
        self.assertEqual(val.parse('abc', []), good('xyz', [], None))
        
    def testGet(self):
        self.assertEqual(p.get.parse('abc', {}), good('abc', {}, 'abc'))
    
    def testItem(self):
        self.assertEqual(p.item.parse(l(range(5)), {}), good(l([1,2,3,4]), {}, 0))
    
    def testLiteral(self):
        val = p.literal(3)
        self.assertEqual(val.parse(l([3,4,5]), {}), good(l([4,5]), {}, 3))
        self.assertEqual(val.parse(l([4,5]), {}), m.zero)
    
    def testCheck(self):
        val = p.get.check(lambda x: len(x) > 3)
        self.assertEqual(val.parse('abcde', []), good('abcde', [], 'abcde'))
        self.assertEqual(val.parse('abc', []), m.zero)
    
    def testMany0(self):
        val = p.literal(3).many0()
        self.assertEqual(val.parse(l([4,4,4]), {}), good(l([4,4,4]), {}, []))
        self.assertEqual(val.parse(l([3,3,4,5]), {}), good(l([4,5]), {}, [3,3]))
    
    def testMany1(self):
        val = p.literal(3).many1()
        self.assertEqual(val.parse(l([4,4,4]), {}), m.zero)
        self.assertEqual(val.parse(l([3,3,4,5]), {}), good(l([4,5]), {}, [3,3]))
    
    def testAll(self):
        val = p.all([p.item, p.literal(2), p.literal(8)])
        self.assertEqual(val.parse(l([3,2,4]), {}), m.zero)
        self.assertEqual(val.parse(l([3,2,8,16]), {}), good(l([16]), {}, [3,2,8]))
    
    def testSeq2R(self):
        val = p.literal(2).seq2R(p.literal(3))
        self.assertEqual(val.parse(l([4,5]), {}), m.zero)
        self.assertEqual(val.parse(l([2,4,5]), {}), m.zero)
        self.assertEqual(val.parse(l([2,3,4]), {}), good(l([4]), {}, 3))
    
    def testSeq2L(self):
        val = p.literal(2).seq2L(p.literal(3))
        self.assertEqual(val.parse(l([4,5]), {}), m.zero)
        self.assertEqual(val.parse(l([2,4,5]), {}), m.zero)
        self.assertEqual(val.parse(l([2,3,4]), {}), good(l([4]), {}, 2))
    
    def testNot0(self):
        val = p.literal(2).not0()
        self.assertEqual(val.parse(l([2,3,4]), {}), m.zero)
        self.assertEqual(val.parse(l([3,4,5]), {}), good(l([3,4,5]), {}, None))
    
    def testNot1(self):
        val = p.literal(2).not1()
        self.assertEqual(val.parse(l([2,3,4]), {}), m.zero)
        self.assertEqual(val.parse(l([3,4,5]), {}), good(l([4,5]), {}, 3))
    
    def testCommit(self):
        val = p.literal(2).commit('bag-agg')
        self.assertEqual(val.parse(l([2,3,4]), 'hi'), good(l([3,4]), 'hi', 2))
        self.assertEqual(val.parse(l([3,4,5]), 'hi'), m.error('bag-agg'))
        