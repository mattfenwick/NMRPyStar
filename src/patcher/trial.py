'''
Created on Apr 29, 2013

@author: mattf
'''
import xeasy.parser as p
import parse.conslist as c
import parse.position as ps

import patcher.star as pstar
import nmrstar.simple.unparser as unp




def xeasy_peakfile_parser(inp):
    return p.xeasy.parse(c.ConsList.fromIterable(ps.addLineCol(inp)), None)


def xeasy_project_parser(hncopath, nhsqcpath):
    with open(hncopath, 'r') as hncofile:
        hnco = hncofile.read()
    with open(nhsqcpath, 'r') as nhsqcfile:
        nhsqc = nhsqcfile.read()
    xhnco = xeasy_peakfile_parser(hnco)
    xnhsqc = xeasy_peakfile_parser(nhsqc)
    if xhnco.status != 'success' or xnhsqc.status != 'success':
        raise ValueError(('hnco or nhsqc parsing failed', xhnco, xnhsqc))
    return pstar.xeasy_in(xhnco.value['result'], xnhsqc.value['result'])

def star_project_dumper(pmodel, starpath):
    text = unp.unparse(pstar.star_out(pmodel))
    print ('shit', text, type(text))
    with open(starpath, 'w') as outfile:
        outfile.write(text)
    return None
