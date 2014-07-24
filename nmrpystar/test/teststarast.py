import unittest as u
from ..starast import Loop, Save, Data, buildLoop, buildSave, buildData, concreteToAST
from ..cleantokens import token
from ..unparse import maybeerror as me
from .testhierarchical import loop, stop, id1, id2, val1, val2, data_o, save_o, save_c, node



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




good = me.MaybeError.pure
def bad(**kwargs):
    return me.MaybeError.error(kwargs)
id3 = token('key', (81, 3), value='matt')
val3 = token('value', (10,10), value='eel')


class TestASTBuilder(u.TestCase):
    
    def testLoop(self):
        cst = node('loop', 1, open=None, close=None, keys=[], values=[])
        ast = Loop([], [])
        self.assertEqual(buildLoop(cst), good(ast))

    def testLoopComplex(self):
        cst = node('loop', 3, open=None, close=None, 
                   keys=[id1, id2],
                   values=[val1, val2])
        ast = Loop(['matt', 'dog'], [['hihi', 'blar']])
        self.assertEqual(buildLoop(cst), good(ast))
    
    def testSave(self):
        cst = node('save', 77, open=save_o, close=None, 
                   datums=[], loops=[])
        save = Save({}, [])
        self.assertEqual(buildSave(cst), good(save))
    
    def testSaveComplex(self):
        cst = node('save', 32, open=save_o, close=None, 
                   datums=[node('datum', 36, key=id1, value=val3), 
                           node('datum', 43, key=id2, value=val2)],
                   loops=[node('loop', 50, keys=[], values=[])])
        save = Save({'matt': 'eel', 'dog': 'blar'}, [Loop([], [])])
        self.assertEqual(buildSave(cst), good(save))
        
    def testData(self):
        cst = node('data', 9, open=data_o, saves=[])
        data = Data('bye', {})
        self.assertEqual(buildData(cst), good(data))
    
    def testDataComplex(self):
        cst = node('data', 3, open=data_o, 
                   saves=[node('save', 5, open=save_o, close=save_c, datums=[], loops=[])])
        data = Data('bye', {'hi': Save({}, [])})
        self.assertEqual(buildData(cst), good(data))
    
    def testFull(self):
        cst = node('data', 8, open=data_o,
                   saves=[node('save', 27, open=save_o, close=save_c, 
                               datums=[node('datum', 36, key=id2, value=val1)],
                               loops=[node('loop', 45, open=loop, close=stop,
                                           keys=[id2, id1], values=[val2, val1, val3, val1])])])
        ast = Data('bye', {'hi': Save({'dog': 'hihi'}, 
                                          [Loop(['dog', 'matt'], [['blar', 'hihi'], ['eel', 'hihi']])])})
        self.assertEqual(concreteToAST(cst), good(ast))


    
class TestErrors(u.TestCase):

    def testLoopDuplicateKeys(self):
        cst = node('loop', 4, open=None, close=None, keys=[id3, id1], values=[])
        self.assertEqual(buildLoop(cst), bad(message='duplicate key', nodetype='loop',
                                               key='matt', first=(81,3), second=(6,6)))
    
    def testLoopBadValueNumber(self):
        cst = node('loop', 5, open=loop, close=None,
                   keys=[id1, id2],
                   values=[val1, val2, val3])
        self.assertEqual(buildLoop(cst),
                         bad(message='number of values must be integer multiple of number of keys', 
                             nodetype='loop', position=(1,1), numkeys=2, numvals=3))
    
    def testLoopNoKeys(self):
        cst = node('loop', 6, open=loop, close=None,
                   keys=[], values=[val3, val2, val1])
        self.assertEqual(buildLoop(cst),
                         bad(message='values but no keys', nodetype='loop', position=(1,1)))
    
    def testSavePropagatesLoopError(self):
        cst = node('save', 28, open=save_o, close=None,
                   datums=[], loops=[node('loop', 36, keys=[id1, id3], values=[])])
        self.assertEqual(buildSave(cst), bad(message='duplicate key', nodetype='loop', 
                                               key='matt', first=(6,6), second=(81,3)))
    
    def testSaveDuplicateKey(self):
        cst = node('save', 17, open=save_o, close=None,
                   datums=[node('datum', 21, key=id3, value=val2),
                           node('datum', 24, key=id1, value=val3)],
                   loops=[])
        self.assertEqual(buildSave(cst), bad(message='duplicate key', nodetype='save',
                                               key='matt', first=(81,3), second=(6,6)))
    
    def testDataRepeatedSaveName(self):
        cst = node('data', 3, open=data_o, 
                   saves=[node('save', 5, open=save_o, close=save_c, datums=[], loops=[]),
                          node('save', 7, open=save_o, close=save_c, datums=[], loops=[])])
        self.assertEqual(buildData(cst), bad(message='duplicate save frame name', nodetype='data',
                                               name='hi', first=(4,4), second=(4,4)))
    
    def testDataPropagateLoopError(self):
        cst = node('data', 29, open=data_o,
                   saves=[node('save', 32, open=save_o, close=save_c, datums=[],
                               loops=[node('loop', 35, open=loop, close=stop, keys=[id1, id3], values=[])])])
        self.assertEqual(buildData(cst), bad(message='duplicate key', nodetype='loop', 
                                               key='matt', first=(6,6), second=(81,3)))
    
    def testDataPropagateSaveError(self):
        cst = node('data', 17, open=data_o,
                   saves=[node('save', 18, open=save_o, close=save_c, loops=[],
                               datums=[node('datum', 23, key=id3, value=val3),
                                       node('datum', 28, key=id1, value=val1)])])
        self.assertEqual(buildData(cst), bad(message='duplicate key', nodetype='save',
                                               key='matt', first=(81,3), second=(6,6)))
