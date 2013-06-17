'''
@author: mattf
'''
import cProfile
import pstats
from .. import fullparse


def readMe():
    with open('nmrpystar/test/bmrb17661.txt', 'r') as f:
        return f.read()


def parseFile(string):
    return fullparse.parse(string)


def fullProfile():
    cProfile.runctx('parseIt(str)', {}, {'parseIt': parseFile, 'str': readMe()}, 'fullprofile.txt')
    return pstats.Stats('fullprofile.txt')


def profileQuery(stats):
    return stats.sort_stats('time').print_stats()