import nmrpystar.astparser as p
import nmrpystar.tokens
import nmrpystar.model as md
import nmrpystar.parse.position as np
import nmrpystar.parse.maybeerror as me
import nmrpystar.parse.conslist as c
import unittest as u



m = me.MaybeError
Token = nmrpystar.tokens.Token
l = c.ConsList.fromIterable

m1, m2 = {'line': 3, 'column': 4}, {'line': 5, 'column': 10}

def good(rest, state, result):
    return m.pure({'rest': rest, 'state': state, 'result': result})
    
loop, stop = Token('loop', None, m1), Token('stop', None, m2)
ident, val = Token('identifier', 'abc', None), Token('value', '123', None)
saveopen, saveclose = Token('saveopen', 'mysave', m1), Token('saveclose', 'save_', m2)
dataopen = Token('dataopen', 'hello1', m2)


class TestParser(u.TestCase):

    def testLoop(self):
        toks = l([loop, ident, val, stop])
        output = good(l([]), None, md.Loop.fromSimple(['abc'], ['123'], m1))
        self.assertEqual(p.loop.parse(toks, None), output)
        
    def testDatum(self):
        toks = l([ident, val, stop])
        output = good(l([stop]), None, ('abc', '123'))
        self.assertEqual(p.datum.parse(toks, None), output)
        
    def testSave(self):
        toks = l([saveopen, ident, val, loop, stop, saveclose, saveopen])
        output = good(l([saveopen]), 
                      None, 
                      ('mysave', md.Save.fromSimple([('abc', '123'), md.Loop.fromSimple([], [], m1)], m1)))
        self.assertEqual(p.save.parse(toks, None), output)
        
    def testData(self):
        toks = l([dataopen, saveopen, ident, val, saveclose])
        output = good(l([]),
                      None,
                      md.Data.fromSimple('hello1', [('mysave', md.Save.fromSimple([('abc', '123')], m1))], m2))
        self.assertEqual(p.data.parse(toks, None), output)

