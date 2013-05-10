import xeasy.model as m
import xeasy.unparser as unp
import unittest as u


def j(x):
    return ''.join(x)


class TestXEasyUnParser(u.TestCase):
    
    def testLine1(self):
        self.assertEqual('# Number of dimensions 3\n', j(unp.line1(3)))
        
    def testDims(self):
        out = '''
# INAME 1 H
# INAME 2 N
'''
        self.assertEqual(out[1:], j(unp.dims(['H', 'N'])))
        
    def testPeakLine(self):
        pk = m.Peak([8.93, 2.24], 1)
        self.assertEqual(' 3 8.93 2.24 1 T          1  0.00e+00 a   0    0    0 0\n', j(unp.peak(3, pk)))
        
    def testXEasy(self):
        out = '''
# Number of dimensions 2
# INAME 1 N
# INAME 2 H
 1 129.394 9.563 1 T          8.92  0.00e+00 a   0    0    0 0
 2 128.745 9.875 1 T          -11.12  0.00e+00 a   0    0    0 0
 3 128.581 9.018 1 T          66.34  0.00e+00 a   0    0    0 0
'''
        self.assertEqual(out[1:], j(unp.xeasy(m.PeakFile(['N', 'H'], {2: m.Peak([128.745, 9.875], -11.12),
                                                                      3: m.Peak([128.581, 9.018], 66.34),
                                                                      1: m.Peak([129.394, 9.563], 8.92)}))))