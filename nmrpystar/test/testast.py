from .. import ast as a
import unittest as u



class TestAST(u.TestCase):

    def testLoop(self):
        myLoop = a.Loop(['a', 'b'], [['0', '1'], ['2', '3']])
        self.assertEqual(myLoop.keys, ['a', 'b'])
        self.assertEqual(myLoop.rows, [['0', '1'], ['2', '3']])
        
    def testLoopExceptions(self):
        self.assertRaises(TypeError, a.Loop, ['a', 'b'], {})
        self.assertRaises(TypeError, a.Loop, ['a', 'b'], range(5))
        self.assertEqual(a.Loop(['a', 'b'], []).rows, [])
    
    def testLoopGetRowAsDict(self):
        lp = a.Loop(['a', 'b'], [['c', 'd'], ['e', 'f']])
        self.assertEqual(lp.getRowAsDict(1), {'a': 'e', 'b': 'f'})

    def testSave(self):
        mySave = a.Save({'a': 'hi', 'b': 'bye'}, [a.Loop(['z'], [['y']])])
        self.assertEqual(mySave.datums['b'], 'bye')
        self.assertEqual(len(mySave.loops), 1)
        
    def testSaveExceptions(self):
        self.assertRaises(TypeError, a.Save, [], [])
        self.assertRaises(TypeError, a.Save, {}, 'oops')
    
    def testData(self):
        myData = a.Data('abc', {'s1': a.Save({'x': 'y'}, [])})
        self.assertEqual(myData.name, 'abc')
        self.assertEqual(myData.saves['s1'].datums.keys(), ['x'])
        
    def testDataExceptions(self):
        self.assertRaises(TypeError, a.Data, 'abc', [])
