

class ConsList(object):

    def __init__(self, seq, start):
        self.seq = seq
        self.start = start
        
    def isEmpty(self):
        return self.start >= len(self.seq)
        
    def first(self):
        if not self.isEmpty():
            return self.seq[self.start]
        raise ValueError('cannot get first element of empty sequence')
        
    def rest(self):
        if not self.isEmpty():
            return ConsList(self.seq, self.start + 1)
        raise ValueError('cannot get rest of empty sequence')
    
    @staticmethod
    def fromIterable(seq):
        return ConsList(seq, 0)
        
    def __eq__(self, other):
        try:
            return self.seq[self.start:] == other.seq[other.start:]
        except:
            return False
        
    def __repr__(self):
        return repr({'type': 'cons list', 'sequence': self.seq[self.start:]})
            
