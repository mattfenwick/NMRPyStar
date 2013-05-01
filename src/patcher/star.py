'''
Created on Apr 29, 2013

@author: mattf
'''
import patcher.model as pmod
import nmrstar.model as nsmod
import xeasy.model as xez


# my model (spectrum) -> star save frame
# have to make sure all star datums are strings
# save frame format definition:
#   - name (in save_<name>)
#   - key/vals:  ??none??
#   - loop:  axes  (axis number, nucleus)
#   - loop:  peaks (peak id, shifts -- don't forget this depends on dimensionality)
#   - loop:  tags  (peak id, tag)
#   - loop:  atomtypes (peak id, atomtype)
def star_spectrum(spec):
    datums = {}
    l_a = nsmod.Loop(['axisnumber', 'nucleus'], zip(map(str, range(1, len(spec.axes) + 1)), spec.axes), None)
    l_p = nsmod.Loop(['peakid'] + ['shift' + str(x + 1) for (x,_) in enumerate(spec.axes)], 
                     [map(str, [pkid] + pk.shifts) for (pkid, pk) in sorted(spec.peaks.iteritems(), key=lambda (k, v): k)], 
                     None)
    tags, aas = [], []
    for (pkid, pk) in spec.peaks.iteritems():
        pid = str(pkid)
        for tag in pk.tags:
            tags.append([pid, tag])
        for aa in pk.atomtypes:
            aas.append([pid, aa])
    l_t = nsmod.Loop(['peakid', 'tag'], tags, None)
    l_aa = nsmod.Loop(['peakid', 'atomtype'], aas, None)
    loops = [l_a, l_p, l_t, l_aa]
    return nsmod.Save(datums, loops, None)

# my model -> star model
def star_out(pmodel):
    save_hnco = star_spectrum(pmodel.spectra['hnco'])
    save_nhsqc = star_spectrum(pmodel.spectra['nhsqc'])
    if len(pmodel.spectra) > 2:
        raise ValueError(('unhandled spectra in Project', pmodel))
    return nsmod.Data(pmodel.name, {'hnco': save_hnco, 'nhsqc': save_nhsqc}, None)


def xeasy_peakfile(xpkfl):
    peaks = {}
    for (pid, pk) in xpkfl.peaks.iteritems():
        peaks[pid] = pmod.Peak(pk.shifts, [], [])
    return pmod.Spectrum(xpkfl.dimnames, peaks)

# xeasy model -> my model
def xeasy_in(xhnco, xnhsqc):
    return pmod.Project('mattsnmrproject', {'hnco': xeasy_peakfile(xhnco), 
                                            'nhsqc': xeasy_peakfile(xnhsqc)})



# single spectrum:   star model -> my model
#   which means save frame
def fromStarSpectrum(saveFrame):
    l_axes, l_peaks, l_tags, l_atomtypes = saveFrame.loops
    axes = [axis_name for (_, axis_name) in l_axes.rows]
    peaks = {}
    for pk in l_peaks.rows:
        peaks[pk[0]] = pmod.Peak(pk[1:], [], [])
    for tg in l_tags.rows:
        peaks[tg[0]].tags.append(tg[1])
    for ats in l_atomtypes.rows:
        peaks[ats[0]].atomtypes.append(ats[1])
    return pmod.Spectrum(axes, peaks)

# star model -> my model
def star_in(sdata):
    return pmod.Project(sdata.name, {'hnco': fromStarSpectrum(sdata.saves['hnco']),
                                     'nhsqc': fromStarSpectrum(sdata.saves['nhsqc'])})
    
def xeasy_peakfile_out(pspec):
    peaks = {}
    for (pkid, pk) in pspec.peaks.iteritems():
        peaks[int(pkid)] = xez.Peak(pk.shifts)
    return xez.PeakFile(pspec.axes, peaks)

# my model -> xeasy model
def xeasy_out(pmodel):
    xhnco = xeasy_peakfile_out(pmodel.spectra['hnco'])
    xnhsqc = xeasy_peakfile_out(pmodel.spectra['nhsqc'])
    return [xhnco, xnhsqc]
