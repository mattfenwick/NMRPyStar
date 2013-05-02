import patcher.model as pm


def addTagAll(tag, spec):
    '''
    Add a tag to all peaks in a spectrum
    '''
    for pk in spec.peaks.values():
        pk.tags.append(tag)

def addTagSome(tag, spec, pkids):
    '''
    Add a tag to some peaks in a spectrum,
    where the peaks are specified by a list
    of peak ids.
    '''
    for pkid in pkids:
        spec.peaks[pkid].tags.append(tag)
        
def filterSpecPeaks(pred, spec):
    '''
    Filter peaks from a spectrum based on a predicate,
    returning a new spectrum.
    '''
    peaks = filter(pred, spec.peaks)
    return pm.Spectrum(spec.axes, peaks)

def peakHasTag(tag):
    '''
    A predicate for checking whether a peak has a tag.
    '''
    return lambda pk: tag in pk.tags

def addAtomtypeAll(aa, spec):
    '''
    Add an atomtype to all peaks in a spectrum
    '''
    for pk in spec.peaks:
        pk.atometypes.append(aa)
