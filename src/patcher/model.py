'''
Created on Apr 29, 2013

@author: mattf
'''


def fmap_dict(f, dic):
    '''
    Apply a function to every value in a dictionary, creating a new
    dictionary with the same size and same keys.
    '''
    return dict((key, f(value)) for (key, value) in dic.iteritems())


def toJson(obj):
    if isinstance(obj, (int, float, basestring)):
        return obj
    if isinstance(obj, list):
        return map(toJson, obj)
    if isinstance(obj, dict):
        return fmap_dict(toJson, obj)
    return obj.toJson()
#    raise TypeError(('unable to convert to JSON value', obj))


class MyBase(object):
    '''
    Provides:
     - conversion to a JSON-compatible object as a dictionary, assuming all fields are JSON-compatible
     - standard __repr__ serialization
     - standard value-based equality
    '''
    
    def toJson(self):
        return toJson(self.__dict__)
    
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


class Spectrum(MyBase):
    '''
    This isn't so much a spectrum as it is a bunch of peaks from the same spectrum
    type.  Tags are responsible for keeping separate 'peaklists'.
    '''
    
    def __init__(self, axes, peaks):
        for (pkid, pk) in peaks.iteritems():
            if not isinstance(pkid, int):
                raise TypeError(('peak id', pkid))
            if len(pk.dims) != len(axes):
                raise ValueError('peak dimensions must match spectral axes')
        self.axes = axes
        self.peaks = peaks
    

class Molecule(MyBase):
    
    def __init__(self, residues):
        if not isinstance(residues, dict):
            raise TypeError(('residues', residues))
        for rid in residues.keys():
            if not isinstance(rid, int):
                raise TypeError(('residue id', rid))
        self.residues = residues
    
    
class SpinSystem(MyBase):
    '''
    Not sure about the residueid relationship since I haven't used it yet:
     - what if spinsystem1 is followed by spinsystem2, but they're assigned
       to non-sequential residues?  Should fragments of spinsystems be
       assigned instead?  I can't answer until I actually get this far.
    '''
    
    def __init__(self, pkids, aatypes, residueids, ssnexts):
        for pkid in pkids:
            if not isinstance(pkid, int):
                raise TypeError(('peak id', pkid))
        self.pkids = pkids
        self.aatypes = aatypes
        for rid in residueids:
            if not isinstance(rid, int):
                raise TypeError(('residue id', rid))
        self.residueids = residueids
        for ssid in ssnexts:
            if not isinstance(ssid, int):
                raise TypeError(('spin system id', ssid))
        self.ssnexts = ssnexts
        
        
class Project(MyBase):
    
    def __init__(self, name, spectra, molecule, spinsystems):
        '''
        Who knows what 'name' means?
        '''
        if not isinstance(spectra, dict):
            raise TypeError(('spectra', spectra))
        for specname in spectra.keys():
            if not isinstance(specname, basestring):
                raise TypeError(('spectrum name', specname))
        if not isinstance(molecule, Molecule):
            raise TypeError(('molecule', molecule))
        if not isinstance(spinsystems, dict):
            raise TypeError(('spin systems', spinsystems))
        for ssid in spinsystems.keys():
            if not isinstance(ssid, int):
                raise TypeError(('spin system id', ssid))
        self.name = name
        self.spectra = spectra
        self.molecule = molecule
        self.spinsystems = spinsystems
