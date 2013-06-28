
_STATUSES = set(['success', 'failure', 'error'])


class MaybeError(object):
    
    def __init__(self, status, value):
        if not status in _STATUSES:
            raise ValueError("invalid MaybeError status: %s" % status)
        self.status = status
        self.value = value

    @staticmethod
    def pure(x):
        return MaybeError('success', x)
    
    @staticmethod
    def error(e):
        return MaybeError('error', e)
        
    def fmap(self, f):
        if self.status == 'success':
            return MaybeError.pure(f(self.value))
        return self
        
    @staticmethod    
    def app(f, *vals):
        args = []
        for v in vals:
            if v.status == 'success':
                args.append(v.value)
            else:
                return v
        return MaybeError.pure(f(*args))
    
    def bind(self, f):
        if self.status == 'success':
            return f(self.value)
        return self
        
    def mapError(self, f):
        if self.status == 'error':
            return MaybeError.error(f(self.value))
        return self
        
    def plus(self, other):
        if self.status == 'failure':
            return other
        return self

    def __repr__(self):
        return repr({
            'type': 'MaybeError', 
            'status': self.status, 
            'value': self.value
        })

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
# defined outside the class b/c it's a constant
MaybeError.zero = MaybeError('failure', None)
