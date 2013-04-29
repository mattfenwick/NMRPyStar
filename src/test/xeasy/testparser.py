'''
Created on Apr 29, 2013

@author: mattf
'''
import xeasy.parser as p
import parse.position as np
import parse.maybeerror as me
import parse.conslist as c
import unittest as u
import xeasy.model as mod


m = me.MaybeError
l = c.ConsList.fromIterable

def good(rest, state, result):
    return m.pure({'rest': rest, 'state': state, 'result': result})

def runParser(parser, inp):
    return parser.parse(l(inp), None)


class TestXEasy(u.TestCase):
    
    def testLine1(self):
        inp = '# Number of dimensions 2\nhello'
        inp1 = np.addLineCol(inp)
        self.assertEqual(good(l(inp1[-5:]), None, 2), runParser(p.line1, inp1))
    
    def testDims(self):
        inp = '# INAME 1 h\n# INAME 2 N\noops'
        inp1 = np.addLineCol(inp)
        self.assertEqual(good(l(inp1[-4:]), None, [(1, 'h'), (2, 'N')]), runParser(p.dims(2), inp1))
        self.assertEqual(me.MaybeError.zero, runParser(p.dims(2), inp1[:20]))
    
    def testHeader(self):
        pass

    def testPeakLine(self):
        inp = ' 12 1.2 3.4 a b 1123\noops'
        inp1 = np.addLineCol(inp)
        self.assertEqual(good(l(inp1[-4:]), None, mod.Peak(12, [1.2, 3.4])), runParser(p.peakline(2), inp1))
#        self.assertEqual(me.MaybeError.zero, runParser(p.dims(2), inp1[:20]))
