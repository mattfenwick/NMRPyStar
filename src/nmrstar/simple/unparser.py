import nmrstar.model as m


# this module (ab)uses locally modifiable state
#   because I couldn't find an existing flattening
#   algorithm that I felt up to implementing, and
#   I felt that repeated `''.join([])` would be 
#   terrible for performance
#
# see http://stackoverflow.com/questions/2158395/flatten-an-irregular-list-of-lists-in-python
#   for a possibly better solution
#
# issues:
#   - surround values in "..."
#   - indentation
#   - empty lines
#   - whether " and \ can go in save/data names and identifier names
#   - escaping "..." values -- ab"c\d -> ab\"c\\d

def sortByFirst(pairs):
    return sorted(pairs, key = lambda x: x[0])

def data(node, chunks):
    chunks.extend(['data_', node.name, '\n'])
    for (savename, saveframe) in sortByFirst(node.saves.iteritems()):
        save(savename, saveframe, chunks)
        
def identifier(key):
    return ['_', key]

def save(name, node, chunks):
    chunks.extend(['\n  save_', name, '\n\n'])
    for (key, val) in sortByFirst(node.datums.iteritems()):
        chunks.append('    ')
        chunks.extend(identifier(key))
        chunks.append(' ')
        chunks.extend(value(val))
        chunks.append('\n')
    for myloop in node.loops:
        loop(myloop, chunks)
    chunks.append('\n  save_\n')
    
SPECIALS = set('"\\')
def escapeVal(val):
    newVal = []
    for c in val:
        if c in SPECIALS:
            newVal.append('\\')
        newVal.append(c)
    return ''.join(newVal)

def value(val):
    return ['"', escapeVal(val), '"', ' ']

def loop(node, chunks):
    chunks.extend(['\n    ', 'loop_', '\n'])
    for key in node.keys:
        chunks.append('      ')
        chunks.extend(identifier(key))
        chunks.append('\n')
    for row in node.rows:
        chunks.append('      ')
        for val in row:
            chunks.extend(value(val))
        chunks.append('\n')
    chunks.append('    stop_\n')


def unparse(node):
    if type(node) != m.Data:
        raise TypeError(('unable to star-unparse value', node))
    chunks = []
    data(node, chunks) # wow, that's ... fugly  :(
    return ''.join(chunks)
