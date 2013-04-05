from parse.maybeerror import MaybeError
import unittest as u

m = MaybeError

def inc(x):
    return x + 1

class Tests(u.TestCase):

    def testPure(self):
        self.assertEqual(m.pure(3).value, 3, "pure value")

    def testFmap(self):
        good, bad, error = m.pure(3), m.zero, m.error('oops')
        self.assertEqual(good.fmap(inc), m.pure(4))
        self.assertEqual(bad.fmap(inc), bad)
        self.assertEqual(error.fmap(inc), error)
        self.assertEqual(good.status, 'success')
        self.assertEqual(good.value, 3)

    def testPlus(self):
        good1, good2, bad, error = m.pure(4), m.pure('hi'), m.zero, m.error('oops')
        # good anything -> good
        # bad anything -> anything
        # error anything -> error
        self.assertEqual(good1.plus(good2), good1)
        self.assertEqual(bad.plus(good2), good2)
        self.assertEqual(error.plus(good1), error)

    def testMapError(self):
        good, bad, error = m.pure(3), m.zero, m.error(4)
        self.assertEqual(good, good.mapError(inc))
        self.assertEqual(bad, bad.mapError(inc))
        self.assertEqual(m.error(5), error.mapError(inc))
