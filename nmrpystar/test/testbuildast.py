from .. import buildast as b
from .. import concrete as c
from .. import ast as a
from ..unparse import maybeerror as me
import unittest as u


good = me.MaybeError.pure
bad = me.MaybeError.error


class TestASTBuilder(u.TestCase):
    
    def testLoop(self):
        l = c.Loop(c.Reserved((3,4), 'loop', None), [], [], 2)
        loop = a.Loop([], [])
        self.assertEqual(b.buildLoop(l), good(loop))
    
    def testLoopComplex(self):
        l = c.Loop(c.Reserved((18, 2), 'loop', None), 
                   [c.Key(5, 'abc'), c.Key(6, 'def')], 
                   [c.Value(7, 'hello'), c.Value(8, 'hi'), c.Value(9, 'away'), c.Value(10, 'uh')], 
                   4)
        loop = a.Loop(['abc', 'def'], [['hello', 'hi'], ['away', 'uh']])
        self.assertEqual(b.buildLoop(l), good(loop))
    
#    def testLoopExceptions(self):
#        self.assertTrue(False)
    
    def testSave(self):
        s = c.Save('hi', [], [], 2)
        save = a.Save({}, [])
        self.assertEqual(b.buildSave(s), good(save))
    
    def testSaveComplex(self):
        s = c.Save('bye', 
                   [c.Datum(c.Key(3, 'k'), c.Value(4, 'v')),
                    c.Datum(c.Key(7, 'x'), c.Value(8, 'omg'))],
                   [c.Loop(c.Reserved((2, 8), 'loop', None), [], [], 6)],
                   2)
        save = a.Save({'k': 'v', 'x': 'omg'}, [a.Loop([], [])])
        self.assertEqual(b.buildSave(s), good(save))
        
    def testData(self):
        d = c.Data(c.Reserved((1,1), 'dataopen', '24'), [])
        data = a.Data('24', {})
        self.assertEqual(b.buildData(d), good(data))
    
    def testLoopDuplicateKeys(self):
        l = c.Loop(c.Reserved((2,4), 'loop', None), 
                   [c.Key(4, 'abc'), c.Key(2, 'def'), c.Key(3, 'abc')], [], 8)
        self.assertEqual(b.buildLoop(l), bad(('loop: duplicate key', 'abc', (2,4))))
    
    def testLoopBadValueNumber(self):
        l = c.Loop(c.Reserved((7,9), 'loop', None), 
                   [c.Key(2, 'a'), c.Key(3, 'bc')], 
                   [c.Value(4, 'hi'), c.Value(5, 'bye'), c.Value(6, 'lye')],
                   7)
        self.assertEqual(b.buildLoop(l), bad(('loop: number of values must be integer multiple of number of keys', 
                                              3, 2, (7,9))))
    
    def testSavePropagatesLoopError(self):
        s = c.Save(1, [], [c.Loop(c.Reserved((1,1), 'loop', None), [c.Key(3, 'a'), c.Key(4, 'a')], [], 5)], 6)
        self.assertEqual(b.buildSave(s), bad(('loop: duplicate key', 'a', (1,1))))
    
    def testSaveDuplicateKey(self):
        s = c.Save(c.Reserved(1, 'saveopen', 'hi'), 
                   [c.Datum(c.Key(2, 'x'), c.Value(3, 'y')),
                    c.Datum(c.Key(4, 'x'), c.Value(5, 'z'))],
                   [],
                   6)
        self.assertEqual(b.buildSave(s), bad(('save: duplicate key', 'x', 1)))
    
    def testDataRepeatedSaveName(self):
        d = c.Data(c.Reserved(18, 'dataopen', 'hi'), 
                   [c.Save(c.Reserved(2, 'saveopen', 's1'), [], [], 3), 
                    c.Save(c.Reserved(4, 'saveopen', 's2'), [], [], 5), 
                    c.Save(c.Reserved(6, 'saveopen', 's1'), [], [], 7)])
        self.assertEqual(b.buildData(d), bad(('data: duplicate save frame name', 's1', 18)))
    
    def testDataPropagateLoopError(self):
        d = c.Data(c.Reserved(99, 'dataopen', 'oo'), 
                   [c.Save(c.Reserved(1, 'saveopen', 'oop'), 
                           [], 
                           [c.Loop(c.Reserved(22, 'loop', None), 
                                   [c.Key(3, 'a'), c.Key(4, 'a')], 
                                   [], 
                                   5)], 
                           6)])
        self.assertEqual(b.buildData(d), bad(('loop: duplicate key', 'a', 22)))
    
    def testDataPropagateSaveError(self):
        d = c.Data(c.Reserved(99, 'dataopen', 'mydata'), 
                   [c.Save(c.Reserved(79, 'saveopen', 'hi'), 
                           [c.Datum(c.Key(2, 'x'), c.Value(3, 'y')),
                            c.Datum(c.Key(4, 'x'), c.Value(5, 'z'))],
                           [],
                           6)])
        self.assertEqual(b.buildData(d), bad(('save: duplicate key', 'x', 79)))
