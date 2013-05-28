'''
Created on May 9, 2013

@author: mattf
'''
import patcher.model as mod


fmap_dict = mod.fmap_dict


def loadPeakDim(dim):
    return mod.PeakDim(dim['shift'], dim['atomtypes'])
    
    
def loadPeak(pk):
    return mod.Peak(map(loadPeakDim, pk['dims']), pk['tags'], float(pk['height']))

    
def loadSpectrum(spec):
    return mod.Spectrum(spec['axes'], dict((int(pkid), loadPeak(pk)) for (pkid, pk) in spec['peaks'].items()))


def loadMolecule(mol):
    return mod.Molecule(mol['residues'])


def loadSpinSystem(ss):
    return mod.SpinSystem(ss['pkids'], ss['aatypes'], ss['residueids'], ss['ssnexts'])


def loadProject(prj):
    '''
    Convert a primitive object graph -- composed dicts, lists, etc., 
    which are presumably from JSON -- to patcher model.
    '''
    return mod.Project(prj['name'], 
                       fmap_dict(loadSpectrum, prj['spectra']), 
                       loadMolecule(prj['molecule']),
                       dict((int(ssid), loadSpinSystem(ss)) for (ssid, ss) in prj['spinsystems'].items()))
