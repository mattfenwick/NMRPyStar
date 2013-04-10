import nmrstar.tokenizer as tok
import nmrstar.tokens
import parse.position as np
import parse.maybeerror as me
import parse.conslist as c
import unittest as u


m = me.MaybeError
Token = nmrstar.tokens.Token
tokenp = tok.token
l = c.ConsList.fromIterable

def good(rest, state, result):
    return m.pure({'rest': rest, 'state': state, 'result': result})

def run(parser, input):
    return parser.parse(input, None) # assume we don't care about the state
    
    
first = {'line': 1, 'column': 1}


class TestTokenizer(u.TestCase):

    def testComment(self):
        input = np.addLineCol("# abc\n123")
        output = good(l(input[5:]), None, Token("comment", " abc", first))
        self.assertEqual(run(tokenp, l(input)), output)

    def testDataOpen(self):
        input = np.addLineCol("data_hello 123abc")
        output = good(l(input[10:]), None, Token("dataopen", "hello", first))
        self.assertEqual(run(tokenp, l(input)), output)
    
    def testSaveOpen(self):
        input = np.addLineCol("save_hello 123abc")
        output = good(l(input[10:]), None, Token("saveopen", "hello", first))
        self.assertEqual(run(tokenp, l(input)), output)
    
    def testSaveClose(self):
        input = np.addLineCol("save_ hello 123abc")
        output = good(l(input[5:]), None, Token("saveclose", "save_", first))
        self.assertEqual(run(tokenp, l(input)), output)
    
    def testLoop(self):
        input = np.addLineCol("loop_ hello 123abc")
        output = good(l(input[5:]), None, Token("loop", "loop_", first))
        self.assertEqual(run(tokenp, l(input)), output)
    
    def testStop(self):
        input = np.addLineCol("stop_ hello 123abc")
        output = good(l(input[5:]), None, Token("stop", "stop_", first))
        self.assertEqual(run(tokenp, l(input)), output)
    
    def testValue(self):
        cases = [["'abc' 123", 5, 'abc', 'single-quoted string'],
                 ["'ab, c'd e' oh", 11, "ab, c'd e", 'tricky single-quoted string'],
                 ['"abc" 123', 5, 'abc', 'double-quoted string'],
                 [';abc\nqrs;xy\n;..???', 13, 'abc\nqrs;xy', 'semicolon string'],
                 ['ab##_"123def\t???', 12, 'ab##_"123def', 'unquoted value']]
        for (str, consumed, value, message) in cases:
            input = np.addLineCol(str)
            output = good(l(input[consumed:]), None, Token("value", value, first))
            print repr(run(tokenp, l(input))) + "\n" + repr(output) + "\n\n"
            self.assertEqual(run(tokenp, l(input)), output, message)
    
    def testWhitespace(self):
        input = np.addLineCol(" \t\t\t  blar")
        output = good(l(input[6:]), None, Token("whitespace", " \t\t\t  ", first))
        self.assertEqual(run(tokenp, l(input)), output)
    
    def testNewlines(self):
        input = np.addLineCol("\n\n\r\f\f\r \t\t\t  blar")
        output = good(l(input[6:]), None, Token("newlines", "\n\n\r\f\f\r", first))
        self.assertEqual(run(tokenp, l(input)), output)
    
    def testIdentifier(self):
        input = np.addLineCol("_abcd123 \t\t\t  blar")
        output = good(l(input[8:]), None, Token("identifier", "abcd123", first))
        self.assertEqual(run(tokenp, l(input)), output)
    
    def testScanner(self):
        self.assertEqual(run(tok.scanner, l(np.addLineCol('"abc'))), 
            m.error({'message': 'unable to parse token', 'position': {'line': 1, 'column': 1}}))
        self.assertEqual(run(tok.scanner, l(np.addLineCol('abc \n "abc'))), 
            m.error({'message': 'unable to parse token', 'position': {'line': 2, 'column': 2}}))
        self.assertEqual(run(tok.scanner, l(np.addLineCol('# abc \n123'))),
            m.pure({'rest': l([]), 'state': None, 'result': [Token('comment', ' abc ', {'line': 1, 'column': 1}),
                                                          Token('newlines', '\n', {'line': 1, 'column': 7}),
                                                          Token('value', '123', {'line': 2, 'column': 1})]}))
    