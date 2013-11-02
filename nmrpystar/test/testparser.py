from .. import parser as p
from ..cleantokens import token
from ..unparse import maybeerror as me
from ..unparse import combinators
import unittest as u


m = me.MaybeError
l = combinators.ConsList

def good(rest, state, result):
    return m.pure({'rest': rest, 'state': state, 'result': result})

def bad(message, position):
    return m.error({'message': message, 'position': position})

def run(parser, i):
    return combinators.run(parser, i, 1)

def node(name, count, **kwargs):
    kwargs['_name'] = name
    kwargs['_state'] = count
    return kwargs

# some tokens
loop = token('reserved', (1,1), keyword='loop')
stop = token('reserved', (2,2), keyword='stop')
save_c = token('reserved', (3,3), keyword='save close')
save_o = token('reserved', (4,4), keyword='save open', value='hi')
data_o = token('reserved', (5,5), keyword='data open', value='bye')
id1 = token('identifier', (6,6), value='matt')
id2 = token('identifier', (7,7), value='dog')
val1 = token('value', (8,8), value='hihi')
val2 = token('value', (9,9), value='blar')


class TestCombinations(u.TestCase):

    def testLoop(self):
        inp = [loop, id1, id2, val1, val2, stop]
        output = good(l([]), 7,
                      node('loop', 1, open=loop, close=stop, keys=[id1, id2], values=[val1, val2]))
        self.assertEqual(run(p.loop, inp), output)

    def testDatum(self):
        inp = [id2, val1, save_c]
        output = good(l([save_c]), 3, 
                      node('datum', 1, key=id2, value=val1))
        self.assertEqual(run(p.datum, inp), output)
    
    def testSaveBasic(self):
        inp = [save_o, save_c, stop]
        output = good(l([stop]), 3,
                      node('save',
                           1, 
                           open=save_o,
                           close=save_c,
                           datums=[],
                           loops=[]))
        self.assertEqual(run(p.save, inp), output)
    
    def testSaveComplex(self):
        inp = [save_o, id1, val2, loop, stop, save_c, save_o]
        output = good(l([save_o]), 7, 
                      node('save',
                           1,
                           open=save_o,
                           close=save_c,
                           datums=[node('datum', 2, key=id1, value=val2)],
                           loops=[node('loop', 4, open=loop, close=stop, keys=[], values=[])]))
        self.assertEqual(run(p.save, inp), output)

    def testDataBasic(self):
        inp = [data_o, id1]
        output = good(l([id1]), 2,
                      node('data',
                           1,
                           open=data_o,
                           saves=[]))
        self.assertEqual(run(p.data, inp), output)
        
    def testDataComplex(self):
        inp = [data_o, save_o, id1, val1, save_c, save_c]
        output = good(l([save_c]), 6,
                      node('data',
                           1,
                           open=data_o,
                           saves=[node('save',
                                       2, 
                                       open=save_o,
                                       close=save_c,
                                       datums=[node('datum', 3, key=id1, value=val1)],
                                       loops=[])]))
        self.assertEqual(run(p.data, inp), output)
        
    def testNMRStar(self):
        inp = [data_o, save_o, save_c]
        output = good(l([]), 4,
                      node('data',
                           1,
                           open=data_o,
                           saves=[node('save', 2, open=save_o, close=save_c, datums=[], loops=[])]))
        self.assertEqual(run(p.nmrstar, inp), output)
    
oops = """        
    def testLoopInvalidContent(self):
        inp = 'loop_ \n  _a _b \n 1 \n save_ stop_'
        output = m.error([('loop', (1,1)), ('expected "stop_"', (4,2))])
        self.assertEqual(run(p.loop, l(inp)), output)
        
    def testDatumMissingValue(self):
        inp = '_abc save_'
        output = m.error([('datum', (1,1)), ('expected value', (1,6))])
        self.assertEqual(run(p.datum, l(inp)), output)
        
    def testLoopMissingStop(self):
        inp = [loop, id1, id2, val1, val2]
        # not sure what the positions should be:
        #   first: the position of the loop open token?
        #   second: the position of the last noticed token?
        output = m.error([('loop', (1,1)), ('loop close', (9,9))])
        self.assertEqual(run(p.loop, inp), output)

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
        
    def testDataInvalidContent(self):
        inp = 'data_me loop_ save_them save_'
        # it just hits the loop_, says, "I don't know how to deal with that",
        #   and doesn't consume it
        output = good(l(inp[8:]), (1,9), 
                      concrete.Data(concrete.Reserved((1, 1), 'dataopen', 'me'), 
                                    []))
        self.assertEqual(run(p.data, l(inp)), output)
        
    def testNMRStarUnconsumedTokensRemaining(self):
        inp = 'data_me loop_ save_them save_'
        output = m.error([('unparsed input remaining', pos(1, 9))])
        self.assertEqual(run(p.nmrstar, l(inp)), output)
    
    def testNMRStarNoOpenData(self):
        inp = '  save_me loop_ stop_ save_'
        output = m.error([('expected data block', (1, 3))])
        self.assertEqual(run(p.nmrstar, l(inp)), output)
"""