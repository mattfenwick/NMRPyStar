'''
Created on May 1, 2013

@author: mattf
'''
import patcher.model as pm


def addTagAll(tag, spec):
    '''
    Add a tag to all peaks in a spectrum
    '''
    for pk in spec.peaks.values():
        pk.tags.append(tag)

def addTagSome(tag, spec, pkids):
    for pkid in pkids:
        try:
            spec.peaks[pkid].tags.append(tag)
        except:
            pass # control flow by exception!  whee!
        
def filterSpecPeaks(pred, spec):
    peaks = filter(pred, spec.peaks)
    return pm.Spectrum(spec.axes, peaks)

def addAtomtypeAll(aa, spec):
    '''
    Add an atomtype to all peaks in a spectrum
    '''
    for pk in spec.peaks:
        pk.atometypes.append(aa)
