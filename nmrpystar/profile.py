'''
@author: mattf
'''
import tokenizer as t
import parse.position as p
import parse.conslist as c
import cProfile
import pstats
import parser as nmp


def tokenizeFile(string):
    return t.scanner.parse(c.ConsList.fromIterable(p.addLineCol(string)), None)


def readMe():
    with open('test/nmrstar/bmrb17661.txt', 'r') as f:
        return f.read()


def parseFile(string):
    return nmp.fullParse(string)


def profile():
    # can't use the following b/c parseFile and readMe need to be in scope:
    #   cProfile.run('parseFile(readMe())', 'profile.txt')
    cProfile.runctx('parseFile(readMe())', {}, {'parseFile': tokenizeFile, 'readMe': readMe}, 'profile.txt')
    return pstats.Stats('profile.txt')


def fullProfile():
    cProfile.runctx('parseIt(str)', {}, {'parseIt': parseFile, 'str': readMe()}, 'fullprofile.txt')
    return pstats.Stats('fullprofile.txt')
