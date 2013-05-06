'''
Created on Apr 29, 2013

@author: mattf
'''

class MyBase(object):
    '''
    Provides:
     - conversion to a JSON-compatible object as a dictionary, assuming all fields are JSON-compatible
     - standard __repr__ serialization
     - standard value-based equality
    '''
    
    def toJson(self):
        return self.__dict__
    
    def __repr__(self):
        return repr(self.toJson())
    
    def __eq__(self, other):
        return self.toJson() == other.toJson()


class PeakDim(MyBase):
    
    def __init__(self, shift, atomtypes):
        self.shift = shift
        self.atomtypes = atomtypes


class Peak(MyBase):
    
    def __init__(self, dims, tags):
        for d in dims:
            if not isinstance(d, PeakDim):
                raise TypeError(('peak dimension', d))
        self.dims = dims
        self.tags = tags
    

class Molecule(MyBase):
    
    def __init__(self, residues):
        if not isinstance(residues, dict):
            raise TypeError(('residues', residues))
        self.residues = residues
    
    
class SpinSystem(MyBase):
    
    def __init__(self, peaks, aatypes, residueids):
        for p in peaks:
            if not isinstance(p, Peak):
                raise TypeError(('peak', p))
        self.peaks = peaks
        self.aatypes = aatypes
        self.residueids = residueids


class Spectrum(MyBase):
    '''
    Hmmm, guess this isn't so much a spectrum as
    it is a bunch of peaks from the same spectrum
    type.  Seems like it's still distinct from the
    traditional meaning of 'peaklist', though, in 
    that multiple normal peaklists would all end
    up in the same 'spectrum', and the tags would
    be responsible for splitting them up into sep
    things.
    '''
    
    def __init__(self, axes, peaks):
        for (pkid, pk) in peaks.iteritems():
            if not isinstance(pkid, int):
                raise TypeError('peak ids must be integers')
            if len(pk.shifts) != len(axes):
                raise ValueError('peak dimensions must match spectral axes')
        self.axes = axes
        self.peaks = peaks
        
        
class Project(MyBase):
    
    def __init__(self, name, spectra):
        '''
        Who knows what name means?  It's just there to appease the
        NMR-Star gods.
        '''
        if not isinstance(spectra, dict):
            raise ValueError('Project needs dict of spectral name - spectra')
        self.name = name
        self.spectra = spectra
