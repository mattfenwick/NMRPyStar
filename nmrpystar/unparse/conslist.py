

class ConsList(object):
    '''
    A data structure that supports constant-time first/rest slicing.
    The input sequence is never copied or modified -- all the slicing
    does is increment a position counter and create a new wrapper.
    '''

    def __init__(self, seq, start):
        self.seq = seq
        self.start = start
        
    def isEmpty(self):
        return self.start >= len(self.seq)
        
    def first(self):
        '''
        Returns first element.  Throws exception if empty.
        '''
        if not self.isEmpty():
            return self.seq[self.start]
        raise ValueError('cannot get first element of empty sequence')
        
    def rest(self):
        '''
        Return ConsList of all but the first element.
        Throws exception if empty.
        '''
        if not self.isEmpty():
            return ConsList(self.seq, self.start + 1)
        raise ValueError('cannot get rest of empty sequence')
    
    def getAsList(self):
        '''
        Return list of remaining elements.
        '''
        return list(self.seq[self.start:])
    
    @staticmethod
    def fromIterable(seq):
        return ConsList(seq, 0)
        
    def __eq__(self, other):
        try:
            return self.getAsList() == other.getAsList()
        except:
            return False
    
    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __repr__(self):
        return repr({
            'type': 'cons list', 
            'sequence': self.getAsList()
        })
