from .. import buildast as b
from .. import ast as a
from ..cleantokens import token
from ..unparse import maybeerror as me
from .testparser import loop, stop, id1, id2, val1, val2, data_o, save_o, save_c, node
import unittest as u


good = me.MaybeError.pure
def bad(**kwargs):
    return me.MaybeError.error(kwargs)
id3 = token('key', (81, 3), value='matt')
val3 = token('value', (10,10), value='eel')


class TestASTBuilder(u.TestCase):
    
    def testLoop(self):
        cst = node('loop', 1, open=None, close=None, keys=[], values=[])
        ast = a.Loop([], [])
        self.assertEqual(b.buildLoop(cst), good(ast))

    def testLoopComplex(self):
        cst = node('loop', 3, open=None, close=None, 
                   keys=[id1, id2],
                   values=[val1, val2])
        ast = a.Loop(['matt', 'dog'], [['hihi', 'blar']])
        self.assertEqual(b.buildLoop(cst), good(ast))
    
    def testSave(self):
        cst = node('save', 77, open=save_o, close=None, 
                   datums=[], loops=[])
        save = a.Save({}, [])
        self.assertEqual(b.buildSave(cst), good(save))
    
    def testSaveComplex(self):
        cst = node('save', 32, open=save_o, close=None, 
                   datums=[node('datum', 36, key=id1, value=val3), 
                           node('datum', 43, key=id2, value=val2)],
                   loops=[node('loop', 50, keys=[], values=[])])
        save = a.Save({'matt': 'eel', 'dog': 'blar'}, [a.Loop([], [])])
        self.assertEqual(b.buildSave(cst), good(save))
        
    def testData(self):
        cst = node('data', 9, open=data_o, saves=[])
        data = a.Data('bye', {})
        self.assertEqual(b.buildData(cst), good(data))
    
    def testDataComplex(self):
        cst = node('data', 3, open=data_o, 
                   saves=[node('save', 5, open=save_o, close=save_c, datums=[], loops=[])])
        data = a.Data('bye', {'hi': a.Save({}, [])})
        self.assertEqual(b.buildData(cst), good(data))
    
    def testFull(self):
        cst = node('data', 8, open=data_o,
                   saves=[node('save', 27, open=save_o, close=save_c, 
                               datums=[node('datum', 36, key=id2, value=val1)],
                               loops=[node('loop', 45, open=loop, close=stop,
                                           keys=[id2, id1], values=[val2, val1, val3, val1])])])
        ast = a.Data('bye', {'hi': a.Save({'dog': 'hihi'}, 
                                          [a.Loop(['dog', 'matt'], [['blar', 'hihi'], ['eel', 'hihi']])])})
        self.assertEqual(b.concreteToAST(cst), good(ast))


    
class TestErrors(u.TestCase):

    def testLoopDuplicateKeys(self):
        cst = node('loop', 4, open=None, close=None, keys=[id3, id1], values=[])
        self.assertEqual(b.buildLoop(cst), bad(message='duplicate key', nodetype='loop',
                                               key='matt', first=(81,3), second=(6,6)))
    
    def testLoopBadValueNumber(self):
        cst = node('loop', 5, open=loop, close=None,
                   keys=[id1, id2],
                   values=[val1, val2, val3])
        self.assertEqual(b.buildLoop(cst),
                         bad(message='number of values must be integer multiple of number of keys', 
                             nodetype='loop', position=(1,1), numkeys=2, numvals=3))
    
    def testLoopNoKeys(self):
        cst = node('loop', 6, open=loop, close=None,
                   keys=[], values=[val3, val2, val1])
        self.assertEqual(b.buildLoop(cst),
                         bad(message='values but no keys', nodetype='loop', position=(1,1)))
    
    def testSavePropagatesLoopError(self):
        cst = node('save', 28, open=save_o, close=None,
                   datums=[], loops=[node('loop', 36, keys=[id1, id3], values=[])])
        self.assertEqual(b.buildSave(cst), bad(message='duplicate key', nodetype='loop', 
                                               key='matt', first=(6,6), second=(81,3)))
    
    def testSaveDuplicateKey(self):
        cst = node('save', 17, open=save_o, close=None,
                   datums=[node('datum', 21, key=id3, value=val2),
                           node('datum', 24, key=id1, value=val3)],
                   loops=[])
        self.assertEqual(b.buildSave(cst), bad(message='duplicate key', nodetype='save',
                                               key='matt', first=(81,3), second=(6,6)))
    
    def testDataRepeatedSaveName(self):
        cst = node('data', 3, open=data_o, 
                   saves=[node('save', 5, open=save_o, close=save_c, datums=[], loops=[]),
                          node('save', 7, open=save_o, close=save_c, datums=[], loops=[])])
        self.assertEqual(b.buildData(cst), bad(message='duplicate save frame name', nodetype='data',
                                               name='hi', first=(4,4), second=(4,4)))
    
    def testDataPropagateLoopError(self):
        cst = node('data', 29, open=data_o,
                   saves=[node('save', 32, open=save_o, close=save_c, datums=[],
                               loops=[node('loop', 35, open=loop, close=stop, keys=[id1, id3], values=[])])])
        self.assertEqual(b.buildData(cst), bad(message='duplicate key', nodetype='loop', 
                                               key='matt', first=(6,6), second=(81,3)))
    
    def testDataPropagateSaveError(self):
        cst = node('data', 17, open=data_o,
                   saves=[node('save', 18, open=save_o, close=save_c, loops=[],
                               datums=[node('datum', 23, key=id3, value=val3),
                                       node('datum', 28, key=id1, value=val1)])])
        self.assertEqual(b.buildData(cst), bad(message='duplicate key', nodetype='save',
                                               key='matt', first=(81,3), second=(6,6)))
    