import nmrpystar.ast as m
import unittest as u


bye = '''

l, s, d = m.Loop.fromSimple, m.Save.fromSimple, m.Data.fromSimple

class TestModel(u.TestCase):

    def testLoop(self):
        self.assertEqual(l(['a', 'b'], range(6)).rows, 
                         [[0, 1], [2, 3], [4, 5]])
        
    def testLoopExceptions(self):
        self.assertRaises(ValueError, l, ['a', 'b'], range(5))
        self.assertRaises(ZeroDivisionError, l, [], range(3))
        self.assertEqual(l(['a', 'b'], []).rows, [])
    
    def testSave(self):
        self.assertEqual(s([]).__dict__, m.Save({}, [], None).__dict__)
        sf1 = s([('a', 3), l([], []), ('b', 22)])
        self.assertEqual(sf1.datums, {'a': 3, 'b': 22})
        self.assertEqual(len(sf1.loops), 1)
        
    def testSaveExceptions(self):
        self.assertRaises(TypeError, s, [3])
        self.assertRaises(ValueError, s, [('a', 3), ('a', 4)])
    
    def testData(self):
        db1 = d('abc', [('save1', s([])), ('save2', s([]))])
        self.assertEqual(db1.name, 'abc')
        self.assertEqual(set(db1.saves.keys()), set(['save1', 'save2']))
        
    def testDataExceptions(self):
        self.assertRaises(TypeError, d, 'abc', [3])
        self.assertRaises(ValueError, d, 'a', [('z', s([])), ('z', s([]))])
'''