from .. import parser as p
from ..unparse import maybeerror as me
from ..unparse import combinators
import unittest as u
notnow = """

m = me.MaybeError
l = combinators.ConsList

def good(rest, state, result):
    return m.pure({'rest': rest, 'state': state, 'result': result})

def bad(message, position):
    return m.error({'message': message, 'position': position})

def run(parser, i, position = (1, 1)):
    return combinators.run(parser, i, position)

def token(ttype, pos, **kwargs):
    kwargs['type'] = ttype
    kwargs['pos'] = pos
    return kwargs

# some tokens
loop = 


class TestCombinations(u.TestCase):

    def testLoop(self):
        inp = '''loop_

            _a
            _bab
            1 2
            "wx" "yz"
          stop_'''
        output = good(l([]), (7, 16), concrete.Loop(concrete.Reserved(pos(1, 1), 'loop', None),
                                                    [concrete.Key(pos(3, 13), 'a'),
                                                     concrete.Key(pos(4, 13), 'bab')],
                                                    [concrete.Value(pos(5, 13), '1'),
                                                     concrete.Value(pos(5, 15), '2'),
                                                     concrete.Value(pos(6, 13), 'wx'),
                                                     concrete.Value(pos(6, 18), 'yz')],
                                                    concrete.Reserved(pos(7, 11), 'stop', None)))
        self.assertEqual(run(p.loop, l(inp)), output)
        
    def testLoopMissingStop(self):
        inp = 'loop_ _a 1 2'
        output = m.error([('loop', (1,1)), ('expected "stop_"', (1, 13))])
        self.assertEqual(run(p.loop, l(inp)), output)
        
    def testLoopInvalidContent(self):
        inp = 'loop_ \n  _a _b \n 1 \n save_ stop_'
        output = m.error([('loop', (1,1)), ('expected "stop_"', (4,2))])
        self.assertEqual(run(p.loop, l(inp)), output)
        
    def testDatum(self):
        inp = '_abc 123  \nt'
        output = good(l(inp[-1:]), (2,1), concrete.Datum(concrete.Key(pos(1, 1), 'abc'), 
                                                   concrete.Value(pos(1, 6), '123')))
        self.assertEqual(run(p.datum, l(inp)), output)
    
    def testDatumMissingValue(self):
        inp = '_abc save_'
        output = m.error([('datum', (1,1)), ('expected value', (1,6))])
        self.assertEqual(run(p.datum, l(inp)), output)
        
    def testSave(self):
        inp = 'save_me save_'
        output = good(l([]), (1,14), 
                      concrete.Save(concrete.Reserved((1, 1), 'saveopen', 'me'),
                                    [], 
                                    [], 
                                    concrete.Reserved((1, 9), 'saveclose', None)))
        self.assertEqual(run(p.save, l(inp)), output)
    
    def testSaveComplex(self):
        inp = 'save_thee  _ab cd loop_ stop_ \nsave_ t'
        output = good(l(inp[-1:]), (2,7), 
                      concrete.Save(concrete.Reserved((1, 1), 'saveopen', 'thee'), 
                                    [concrete.Datum(concrete.Key(pos(1, 12), 'ab'),
                                                    concrete.Value(pos(1, 16), 'cd'))],
                                    [concrete.Loop(concrete.Reserved((1, 19), 'loop', None), 
                                                   [], 
                                                   [], 
                                                   concrete.Reserved((1, 25), 'stop', None))],
                                    concrete.Reserved((2, 1), 'saveclose', None)))
        self.assertEqual(run(p.save, l(inp)), output)

    def testSaveUnclosed(self):
        inp = 'save_me _ab 12 '
        output = m.error([('save', (1, 1)), ('expected "save_"', (1, 16))])
        self.assertEqual(run(p.save, l(inp)), output)
        
    def testSaveInvalidContent(self):
        inp = 'save_me _ab \n12 stop_ save_'
        output = m.error([('save', (1,1)), ('expected "save_"', (2, 4))])
        self.assertEqual(run(p.save, l(inp)), output)
    
    def testSaveDatumAfterLoop(self):
        inp = "save_me \n_a b \nloop_ _x y stop_ \n _m n save_"
        output = m.error([('save', (1, 1)), ('expected "save_"', (4,2))])
        self.assertEqual(run(p.save, l(inp)), output)
        
    def testData(self):
        inp = 'data_toks save_us \nsave_ t'
        output = good(l(inp[-1:]), (2,7), 
                      concrete.Data(concrete.Reserved((1,1), 'dataopen', 'toks'),
                                    [concrete.Save(concrete.Reserved((1,11), 'saveopen', 'us'),
                                                   [], 
                                                   [], 
                                                   concrete.Reserved((2, 1), 'saveclose', None))]))
        self.assertEqual(run(p.data, l(inp)), output)
        
    def testDataInvalidContent(self):
        inp = 'data_me loop_ save_them save_'
        # it just hits the loop_, says, "I don't know how to deal with that",
        #   and doesn't consume it
        output = good(l(inp[8:]), (1,9), 
                      concrete.Data(concrete.Reserved((1, 1), 'dataopen', 'me'), 
                                    []))
        self.assertEqual(run(p.data, l(inp)), output)
        
    def testNMRStar(self):
        inp = ' data_me save_you \nsave_ # uh-oh?? \n '
        output = good(l([]), (3,2), 
                      concrete.Data(concrete.Reserved((1,2), 'dataopen', 'me'),
                                    [concrete.Save(concrete.Reserved((1, 10), 'saveopen', 'you'), 
                                                   [], 
                                                   [], 
                                                   concrete.Reserved((2, 1), 'saveclose', None))]))
        self.assertEqual(run(p.nmrstar, l(inp)), output)
    
    def testNMRStarUnconsumedTokensRemaining(self):
        inp = 'data_me loop_ save_them save_'
        output = m.error([('unparsed input remaining', pos(1, 9))])
        self.assertEqual(run(p.nmrstar, l(inp)), output)
    
    def testNMRStarNoOpenData(self):
        inp = '  save_me loop_ stop_ save_'
        output = m.error([('expected data block', (1, 3))])
        self.assertEqual(run(p.nmrstar, l(inp)), output)
"""