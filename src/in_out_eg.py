'''
Created on May 3, 2013

@author: mattf
'''
import patcher.trial as pt
import patcher.model as pmod



q = pt.star_in('../../PeakPick/proj.star')

old = q.spectra['nhsqc']
q.spectra['nhsqc'] = pmod.Spectrum(old.axes, dict(filter(lambda (_,pk): 'backbone amide' not in pk.tags, old.peaks.items())))


pt.xeasy_out(q, {'nhsqc': 'nhsqc.txt'})