'''
Created on May 9, 2013

@author: mattf
'''
import patcher.trial as pt
import patcher.loader as pl
import json



def dumpProject(path, proj):
    with open(path, 'w') as outfile:
        outfile.write(json.dumps(proj.toJson()))


def loadProject(path):
    with open(path, 'r') as infile:
        return pl.loadProject(json.loads(infile.read()))



# ba = pt.xeasy_in('mynameismatt', {'nhsqc': 'nhsqc.xez', 'hnco': 'hnco.xez'})
ba = pt.xeasy_in('mynameismatt', {'nhsqc': 'nhsqc.txt', 'hnco': 'hnco.txt'})
dumpProject('outpath2.txt', ba)


z = loadProject('outpath2.txt')
pt.xeasy_out(z, {'nhsqc': 'nhsqc2.txt', 'hnco': 'hnco2.txt'})


print 'are they equal? ', ba == z