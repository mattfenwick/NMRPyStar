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


reload(pc)


def xeasy_peakfile_parser(inp):
    return p.xeasy.parse(c.ConsList.fromIterable(ps.addLineCol(inp)), None)


def xeasy_in(projname, paths):
    xpkfls = {}
    for (name, path) in paths.items():
        with open(path, 'r') as infile:
            r = xeasy_peakfile_parser(infile.read())
            if r.status != 'success':
                raise ValueError((name + ' parsing failed', r))
            xpkfls[name] = r.value['result']
    return pc.xez2patch(projname, xpkfls)

def xeasy_out(pmodel, paths):
    '''
    Expects a spectrum for each path
    '''
    spectra = pc.patch2xez(pmodel)
    for (name, path) in paths.iteritems():
        spectrum = spectra[name]
        with open(path, 'w') as outfile:
            outfile.write(xunp.xeasy(spectrum))

def star_in(starpath):
    with open(starpath, 'r') as starfile:
        star = nsp.fullParse(starfile.read())
    if star.status != 'success':
        raise ValueError(('unable to parse star project file', star))
    return pc.star2patch(star.value['result'])

def star_out(pmodel, starpath):
    text = unp.unparse(pc.patch2star(pmodel))
    with open(starpath, 'w') as outfile:
        outfile.write(text)
    return None


def xez_to_star(paths, star):
    q = xeasy_in('mattsnmrproject', paths)
    star_out(q, star)

def star_to_xez(paths, star):
    q = star_in(star)
    xeasy_out(q, paths)


# some more examples
def star_filter_hsqc_to_xez(nhsqc, star, tag):
    q = star_in(star)
    new_nhsqc = ut.filterSpecPeaks(ut.peakHasTag(tag), q.spectra['nhsqc'])
    q.spectra['nhsqc'] = new_nhsqc
    xeasy_out(q, {'nhsqc': nhsqc})
