from ..ast import Loop, Save, Data
import unittest as u



class TestAST(u.TestCase):

    def testLoop(self):
        myLoop = Loop(['a', 'b'], [['0', '1'], ['2', '3']])
        self.assertEqual(myLoop.keys, ['a', 'b'])
        self.assertEqual(myLoop.rows, [['0', '1'], ['2', '3']])
        
    def testLoopExceptions(self):
        self.assertRaises(TypeError, Loop, ['a', 'b'], {})
        self.assertRaises(TypeError, Loop, ['a', 'b'], range(5))
        self.assertRaises(ValueError, Loop, ['a', 'a'], [])
        self.assertRaises(ValueError, Loop, ['a', 'b'], [[]])
        self.assertRaises(TypeError, Loop, 'not a list!', [])
    
    def testLoopFields(self):
        self.assertEqual(Loop(['a', 'b'], []).rows, [])
    
    def testLoopGetRowAsDict(self):
        lp = Loop(['a', 'b'], [['c', 'd'], ['e', 'f']])
        self.assertEqual(lp.getRowAsDict(1), {'a': 'e', 'b': 'f'})

    def testSave(self):
        mySave = Save({'a': 'hi', 'b': 'bye'}, [Loop(['z'], [['y']])])
        self.assertEqual(mySave.datums['b'], 'bye')
        self.assertEqual(len(mySave.loops), 1)
        
    def testSaveExceptions(self):
        self.assertRaises(TypeError, Save, [], [])
        self.assertRaises(TypeError, Save, {}, 'oops')
    
    def testData(self):
        myData = Data('abc', {'s1': Save({'x': 'y'}, [])})
        self.assertEqual(myData.name, 'abc')
        self.assertEqual(myData.saves['s1'].datums.keys(), ['x'])
        
    def testDataExceptions(self):
        self.assertRaises(TypeError, Data, 'abc', [])
