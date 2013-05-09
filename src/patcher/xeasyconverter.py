import patcher.model as pmod
import xeasy.model as xmod
from patcher.util import fmap_dict


def _spectrum_to_xeasy(pspec):
    peaks = {}
    for (pkid, pk) in pspec.peaks.iteritems():
        peaks[int(pkid)] = xmod.Peak(pk.shifts)
    return xmod.PeakFile(pspec.axes, peaks)

def patch2xez(pmodel):
    return fmap_dict(_spectrum_to_xeasy, pmodel.spectra)


def _xeasy_to_spectrum(xpkfl):
    peaks = {}
    for (pid, pk) in xpkfl.peaks.iteritems():
        peaks[pid] = pmod.Peak(pk.shifts, tags = [])
    return pmod.Spectrum(xpkfl.dimnames, peaks)
    
def xez2patch(projname, peakfiles):
    return pmod.Project(projname, fmap_dict(_xeasy_to_spectrum, peakfiles))