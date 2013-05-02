'''
Created on Apr 29, 2013

@author: mattf
'''
import xeasy.parser as p
import parse.conslist as c
import parse.position as ps

import patcher.util as ut
import patcher.converters as pc
import nmrstar.parser as nsp
import nmrstar.simple.unparser as unp
import xeasy.unparser as xunp



def xeasy_peakfile_parser(inp):
    return p.xeasy.parse(c.ConsList.fromIterable(ps.addLineCol(inp)), None)

def star_projectfile_parser(inp):
    return nsp.fullParse(inp)


def xeasy_project_parser(paths):
    xpkfls = {}
    for (name, path) in paths:
        with open(path, 'r') as infile:
            r = xeasy_peakfile_parser(infile.read())
            if r.status != 'success':
                raise ValueError((name + ' parsing failed', r))
            xpkfls[name] = r
    return pc.xez2patch('mattsnmrproject', xpkfls)

def star_project_dumper(pmodel, starpath):
    text = unp.unparse(pc.patch2star(pmodel))
    with open(starpath, 'w') as outfile:
        outfile.write(text)
    return None

def xez_2_star_test():
    q = xeasy_project_parser({'hnco': 'hnco_peaks.xeasy', 'nhqc': 'peaks.xeasy'})
    star_project_dumper(q, 'proj_star.txt')
    
def xez_to_star(hnco, nhsqc, star):
    q = xeasy_project_parser({'hnco': hnco, 'nhsqc': nhsqc})
    star_project_dumper(q, star)



def star_project_parser(starpath):
    with open(starpath, 'r') as starfile:
        star = star_projectfile_parser(starfile.read())
    if star.status != 'success':
        raise ValueError(('unable to parse star project file', star))
    return pc.star2patch(star.value['result'])

def xeasy_project_dumper(pmodel, paths):
    spectra = pc.patch2xez(pmodel)
    for (name, spectrum) in spectra:
        path = paths[name]
        with open(path, 'w') as outfile:
            outfile.write(xunp.xeasy(spectrum))

def star_2_xez_test():
    q = star_project_parser('proj_star.txt')
    xeasy_project_dumper(q, {'hnco': 'hnco_out.txt', 'nhsqc': 'nhsqc_out.txt'})

def star_to_xez(hnco, nhsqc, star):
    q = star_project_parser(star)
    # <- here:  cut some peaks/spectra out
    xeasy_project_dumper(q, {'hnco': hnco, 'nhsqc': nhsqc})

def star_hsqc_to_xez(nhsqc, star, tag):
    q = star_project_parser(star)
    new_nhsqc = ut.filterSpecPeaks(ut.peakHasTag(tag), q.spectra['nhsqc'])
    q.spectra['nhsqc'] = new_nhsqc
    xeasy_project_dumper(q, {'hnco': 'dontcare.txt', 'nhsqc': nhsqc})
