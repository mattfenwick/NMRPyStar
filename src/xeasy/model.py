
class PeakFile(object):

    def __init__(self, dimnames, peaks):
        for (_, p) in peaks.iteritems():
            if len(p.shifts) != len(dimnames):
                raise ValueError('PeakFile dimensions must match peak dimensions')
        self.dimnames = dimnames
        self.peaks = peaks

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return repr(self.__dict__)
    
    @staticmethod
    def fromSimple(dimnames, peaklines):
        peaks = {}
        for (pid, peak) in peaklines:
            if peaks.has_key(pid):
                raise ValueError(('duplicate peak id', pid))
            peaks[pid] = peak
        return PeakFile(dimnames, peaks)


class Peak(object):

    def __init__(self, shifts):
        self.shifts = shifts

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return repr(self.__dict__)
