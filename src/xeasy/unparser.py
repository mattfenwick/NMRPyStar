

def peak(pid, pk):
    chunks = [' ', str(pid)]
    for s in pk.shifts:
        chunks.extend([' ', str(s)])
    # not sure what '1' and 'T' mean
    chunks.append(' 1 T          0.000e+00  0.00e+00 a   0    0    0 0\n')
    return chunks
    
def dims(dimNames):
    chunks = []
    i = 1
    for name in dimNames:
        chunks.extend(['# INAME ', str(i), ' ', name, '\n'])
        i += 1
    return chunks

def line1(n):
    return ['# Number of dimensions ', str(n), '\n']    
    
def xeasy(model):
    chunks = []
    chunks.extend(line1(len(model.dimnames)))
    chunks.extend(dims(model.dimnames))
    for (pid, p) in sorted(model.peaks.iteritems(), key=lambda x: x[0]):
        chunks.extend(peak(pid, p))
    return ''.join(chunks)
