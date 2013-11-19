'''
@author: matt
'''
from ...examples import loading
import unittest


class TestLoading(unittest.TestCase):
    
    def testFromString(self):
        z = loading.parseString()
        self.assertEqual(z.status, 'success')
        data = z.value[1]
        self.assertEqual(data.name, 'startthedata')
        self.assertEqual(len(data.saves), 1)
        self.assertEqual(data.saves['firstsave'].loops[0].keys, ['id1', 'id2'])

    def testFromFile(self):
        z = loading.parseFile('bmrb17661.txt')
        print z.value
        self.assertEqual(z.status, 'success')
        # no point in continuing with the tests if the parsing failed!
        data = z.value[1]
        self.assertEqual(data.name, '17661')
        self.assertEqual(len(data.saves), 19)
        self.assertEqual(len(data.saves['entry_information'].datums), 16)
        self.assertEqual(len(data.saves['NMRView'].loops), 2)
    
    def testFromUrl(self):
        z = loading.parseUrl()
        self.assertEqual(z.status, 'success')
        data = z.value[1]
        self.assertEqual(data.name, '248')
        self.assertEqual(len(data.saves), 13)
        self.assertEqual(len(data.saves['chemical_shift_assignment_data_set_one'].loops[1].keys), 24)
        self.assertEqual(len(data.saves['chemical_shift_assignment_data_set_one'].loops[1].rows), 103)
