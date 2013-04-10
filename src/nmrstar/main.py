import nmrstar.tokenizer as t
import parse.position as p
import parse.conslist as c
import cProfile
import pstats
import nmrstar.parser as nmp


def parseFile(input):
    return t.scanner.parse(c.ConsList.fromIterable(p.addLineCol(input)), None)
    
    
def readMe():
    with open('test/nmrstar/bmrb17661.txt', 'r') as f:
        return f.read()
        
        
def profile():
    # can't use the following b/c parseFile and readMe need to be in scope:
    #   cProfile.run('parseFile(readMe())', 'profile.txt')
    cProfile.runctx('parseFile(readMe())', {}, {'parseFile': parseFile, 'readMe': readMe}, 'profile.txt')
    return pstats.Stats('profile.txt')
    
    
def fullProfile():
    cProfile.runctx('parseIt(str)', {}, {'parseIt': nmp.parse, 'str': readMe()}, 'fullprofile.txt')
    return pstats.Stats('fullprofile.txt')
