'''
Created on Apr 29, 2013

@author: mattf
'''


class PeakFile(object):

    def __init__(self, dimnames, peaks):
        for p in peaks:
            if len(p.shifts) != len(dimnames):
                raise ValueError('PeakFile dimensions must match peak dimensions')
        self.dimnames = dimnames
        self.peaks = peaks

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return repr(self.__dict__)


class Peak(object):

    def __init__(self, pid, shifts):
        self.id = pid
        self.shifts = shifts

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return repr(self.__dict__)
