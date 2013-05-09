import patcher.model as pmod
import nmrstar.model as nmod


fmap_dict = pmod.fmap_dict


def _save_to_spectrum(saveFrame):
    l_axes, l_peaks, l_tags, l_atomtypes = saveFrame.loops
    axes = [axis_name for (_, axis_name) in l_axes.rows]
    peaks = {}
    for pk in l_peaks.rows:
        peaks[int(pk[0])] = pmod.Peak(map(float, pk[1:]), [], [])
    for tg in l_tags.rows:
        peaks[int(tg[0])].tags.append(tg[1]) # peaks.has_key(tg[0]) ?
    for ats in l_atomtypes.rows:
        peaks[int(ats[0])].atomtypes.append(ats[1]) # peaks.has_key(ats[0]) ?
    return pmod.Spectrum(axes, peaks)

def star2patch(sdata):
    return pmod.Project(sdata.name, fmap_dict(_save_to_spectrum, sdata.saves))


# my model (spectrum) -> star save frame
# have to make sure all star datums are strings
# save frame format definition:
#   - name (in save_<name>)
#   - key/vals:  ??none??
#   - loop:  axes  (axis number, nucleus)
#   - loop:  peaks (peak id, shifts -- don't forget this depends on dimensionality)
#   - loop:  tags  (peak id, tag)
#   - loop:  atomtypes (peak id, atomtype)
def _spectrum_to_save(spec):
    datums = {}
    l_a = nmod.Loop(['axisnumber', 'nucleus'], zip(map(str, range(1, len(spec.axes) + 1)), spec.axes), None)
    l_p = nmod.Loop(['peakid'] + ['shift' + str(x + 1) for (x,_) in enumerate(spec.axes)], 
                     [map(str, [pkid] + pk.shifts) for (pkid, pk) in sorted(spec.peaks.iteritems(), key=lambda (k, v): k)], 
                     None)
    tags, aas = [], []
    for (pkid, pk) in spec.peaks.iteritems():
        pid = str(pkid)
        for tag in pk.tags:
            tags.append([pid, tag])
        for aa in pk.atomtypes:
            aas.append([pid, aa])
    l_t = nmod.Loop(['peakid', 'tag'], tags, None)
    l_aa = nmod.Loop(['peakid', 'atomtype'], aas, None)
    loops = [l_a, l_p, l_t, l_aa]
    return nmod.Save(datums, loops, None)

def patch2star(pmodel):
    spectra = fmap_dict(_spectrum_to_save, pmodel.spectra)
    return nmod.Data(pmodel.name, spectra, None)
