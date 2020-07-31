import cProfile
import pstats
from nmrpystar.examples import loading


def parseFile(path):
    return loading.parseFile(path)


def fullProfile():
    cProfile.runctx('parseIt(path)', {}, {'parseIt': parseFile, 'path': 'bmrb17661.txt'}, 'fullprofile.txt')
    return pstats.Stats('fullprofile.txt')


def profileQuery(stats):
    return stats.sort_stats('time').print_stats()