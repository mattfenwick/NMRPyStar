import nmrstar.model as m
import nmrstar.simple.unparser as unp
import unittest as u


def j(x):
    return ''.join(x)


class TestUnparser(u.TestCase):

    def testIdentifier(self):
        self.assertEqual(j(unp.identifier('abc')), '_abc')
        self.assertEqual(j(unp.identifier('ab"cd\\')), '_ab"cd\\')

    def testIdentifierWhitespace(self):
        # should not allow spaces in identifier names
        self.assertRaises(Exception, lambda: unp.identifier('ab cd'))

    def testValue(self):
        self.assertEqual(j(unp.value('abc')), '"abc"')
        self.assertEqual(j(unp.value('a"\\b')), '"a\\"\\\\b"')
        self.assertEqual(j(unp.value('a \n')), '"a \n"')

    def testDatum(self):
        # indentation, space, newline
        self.assertEqual(j(unp.datum("abc", '123')), '    _abc "123"\n')

    def testLoop(self):
        # indentation, loop_/stop_ tokens, space separators, ?
        l1 = m.Loop([], [], None)
        self.assertEqual(j(unp.loop(l1)), '    loop_\n    stop_\n')
        l2 = m.Loop.fromSimple(['abc', 'def'], ['123', '456', 'hi', 'bye'])
        s2 = '''
    loop_
      _abc
      _def
      "123" "456" 
      "hi" "bye" 
    stop_
'''            # yes, the trailing spaces are intended to be there
        self.assertEqual(j(unp.loop(l2)), s2[1:])  # skip opening \n

    def testSave(self):
        s2 = ('us', m.Save({}, [m.Loop([], [], None)], None))
        up2 = '''
  save_us


    loop_
    stop_

  save_
'''
        self.assertEqual(j(unp.save(*s2)), up2[1:])
        s1 = ('me', m.Save({'ab': '12', 'cd': '34'},
                           [m.Loop([], [], None), m.Loop([], [], None)],
                           None))
        up1 = '''
  save_me

    _ab "12"
    _cd "34"

    loop_
    stop_

    loop_
    stop_

  save_
'''
        self.assertEqual(j(unp.save(*s1)), up1[1:])  # skip opening \n
        # save names should not have whitespace
        self.assertRaises(ValueError, lambda: j(unp.save('x y', m.Save({}, [], None))))

    def testData(self):
        d1 = m.Data('hi', {'ab': m.Save({}, [], None)}, None)
        ud1 = '''
data_hi

  save_ab


  save_
'''
        self.assertEqual(unp.unparse(d1), ud1[1:])
        self.assertRaises(ValueError, lambda: j(unp.data(m.Data('a b', {}, None))))
