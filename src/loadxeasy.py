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



ba = pt.xeasy_in('mynameismatt', {'nhsqc': 'nhsqc.xez', 'hnco': 'hnco.xez'})
dumpProject('outpath.txt', ba)
