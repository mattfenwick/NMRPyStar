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
        self.assertEqual(good(l(inp1[-4:]), None, ['h', 'N']), runParser(p.dims(2), inp1))
        self.assertEqual(me.MaybeError.zero, runParser(p.dims(2), inp1[:20]))
    
    def testPeakLine(self):
        inp = ' 12 1.2 3.4 a b 1123\noops'
        inp1 = np.addLineCol(inp)
        self.assertEqual(good(l(inp1[-4:]), None, (12, mod.Peak([1.2, 3.4]))), runParser(p.peakline(2), inp1))
#        self.assertEqual(me.MaybeError.zero, runParser(p.dims(2), inp1[:20]))

    def testXEeasy(self):
        inp = '''
# Number of dimensions 1
# INAME 1 H
 1 8.795 1 T          0.000e+02  0.00e+00 a   0    0    0    0 0
 2 7.229 1 T          0.000e+02  0.00e+00 a   0    0    0    0 0
 3 6.243 1 T          0.000e+02  0.00e+00 a   0    0    0    0 0
 4 7.781 1 T          0.000e+02  0.00e+00 a   0    0    0    0 0
'''
        inp1 = np.addLineCol(inp[1:])
        self.assertEqual(good(l([]), None, mod.PeakFile(['H'], {1: mod.Peak([8.795]), 2: mod.Peak([7.229]),
                                                                3: mod.Peak([6.243]), 4: mod.Peak([7.781])})), runParser(p.xeasy, inp1))
