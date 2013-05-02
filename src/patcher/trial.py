'''
Created on Apr 29, 2013

@author: mattf
'''
import xeasy.parser as p
import parse.conslist as c
import parse.position as ps

import patcher.star as pstar
import nmrstar.parser as nsp
import nmrstar.simple.unparser as unp
import xeasy.unparser as xunp


reload(pstar) # repl hack


def xeasy_peakfile_parser(inp):
    return p.xeasy.parse(c.ConsList.fromIterable(ps.addLineCol(inp)), None)

def star_projectfile_parser(inp):
    return nsp.fullParse(inp)


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
    with open(starpath, 'w') as outfile:
        outfile.write(text)
    return None

def xez_2_star_test():
    q = xeasy_project_parser('hnco_peaks.xeasy', 'peaks.xeasy')
    star_project_dumper(q, 'proj_star.txt')
    
def xez_to_star(hnco, nhsqc, star):
    q = xeasy_project_parser(hnco, nhsqc)
    star_project_dumper(q, star)



def star_project_parser(starpath):
    with open(starpath, 'r') as starfile:
        star = star_projectfile_parser(starfile.read())
    if star.status != 'success':
        raise ValueError(('unable to parse star project file', star))
    return pstar.star_in(star.value['result'])

def xeasy_project_dumper(pmodel, hncopath, nhsqcpath):
    hnco, nhsqc = pstar.xeasy_out(pmodel)
    with open(hncopath, 'w') as hncoout:
        hncoout.write(xunp.xeasy((hnco)))
    with open(nhsqcpath, 'w') as nhsqcout:
        nhsqcout.write(xunp.xeasy((nhsqc)))

def star_2_xez_test():
    q = star_project_parser('proj_star.txt')
    xeasy_project_dumper(q, 'hnco_out.txt', 'nhsqc_out.txt')

def star_to_xez(hnco, nhsqc, star):
    q = star_project_parser(star)
    xeasy_project_dumper(q, hnco, nhsqc)
