import patcher.model as pmod
import xeasy.model as xmod


fmap_dict = pmod.fmap_dict


def _spectrum_to_xeasy(pspec):
    peaks = {}
    for (pkid, pk) in pspec.peaks.iteritems():
        shifts = [p.shift for p in pk.dims]
        peaks[int(pkid)] = xmod.Peak(shifts, pk.height)
    return xmod.PeakFile(pspec.axes, peaks)

def patch2xez(pmodel):
    return fmap_dict(_spectrum_to_xeasy, pmodel.spectra)


def _xeasy_to_spectrum(xpkfl):
    peaks = {}
    for (pid, pk) in xpkfl.peaks.iteritems():
        dims = [pmod.PeakDim(s, []) for s in pk.shifts]
        peaks[pid] = pmod.Peak(dims, tags = [], height = pk.height)
    return pmod.Spectrum(xpkfl.dimnames, peaks)
    
def xez2patch(projname, peakfiles):
    return pmod.Project(projname, fmap_dict(_xeasy_to_spectrum, peakfiles), pmod.Molecule({}), {})