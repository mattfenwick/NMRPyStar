'''
@author: matt
'''
from ..cleantokens import clean_token, token
import unittest as u



class TestCleanTokens(u.TestCase):

    def testUnquoted(self):
        r, v = "reserved", "value"
        cases = [
            ["dAta_hello",   r, "data open",  "hello"        , 'data open'                 ],
            ["Save_bye",     r, "save open",  "bye"          , 'save open'                 ],
            ["saVE_",        r, "save close", None           , 'save close'                ],
            ["STOP_",        r, "stop",       None           , 'stop'                      ],
            ["loop_",        r, "loop",       None           , 'loop open'                 ],
            ["LoOp_",        r, "loop",       None           , 'keywords: case insensitive'],
            ["GLOBAl_",      v, None,         "GLOBAl_"      , 'uq: global_'               ],
            ["345",          v, None,         '345'          , 'uq: number'                ],
            ["abc",          v, None,         'abc'          , 'uq: alphas'                ],
            ['ab##_"123def', v, None,         'ab##_"123def' , 'uq: special chars'         ],
            ["loop_uh-oh",   v, None,         'loop_uh-oh'   , 'uq: start with loop_'      ],
            ["stop_def",     v, None,         'stop_def'     , 'uq: start with stop_'      ],
            ['global_"1',    v, None,         'global_"1'    , 'uq: start with global_'    ],
            ['data_',        v, None,         'data_'        , 'uq: data_'                 ]
        ]
        for (inp, name, my_type, value, message) in cases:
            res = clean_token({'_name': 'unquoted', '_state': None, 'first': inp[0], 'rest': list(inp[1:])})
            print message, res
            if name == 'reserved':
                if my_type in ['save open', 'data open']:
                    self.assertEqual(token('reserved', None, keyword=my_type, value=value), res)
                else:
                    self.assertEqual(token('reserved', None, keyword=my_type), res)
            elif name == 'value':
                self.assertEqual(token('value', None, value=value), res)
            else:
                raise ValueError('for completeness -- but should not happen')
    
    def testIdentifier(self):
        self.assertEqual(token('identifier', None, value='abcd'),
                         clean_token(dict(_name='identifier', _state=None, open='_', value=list('abcd'))))
    
    def testScString(self):
        self.assertEqual(token('value', None, value='123'),
                         clean_token(dict(_name='scstring', _state=None, 
                                          open=';', close=list('\n;'), value=list('123'))))

    def testSqString(self):
        self.assertEqual(token('value', None, value='123'),
                         clean_token(dict(_name='sqstring', _state=None, 
                                          open="'", close="'", value=list('123'))))

    def testDqString(self):
        self.assertEqual(token('value', None, value='123'),
                         clean_token(dict(_name='dqstring', _state=None, 
                                          open='"', close='"', value=list('123'))))
