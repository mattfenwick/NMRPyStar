import nmrstar.model as m


# see http://stackoverflow.com/questions/2158395/flatten-an-irregular-list-of-lists-in-python
#   for a possibly better solution to nested list flattening
#
# issues:
#   - surround values in "..."
#   - indentation
#   - empty lines
#   - whether " and \ can go in save/data names and identifier names
#   - escaping "..." values -- ab"c\d -> ab\"c\\d

def sortByFirst(pairs):
    return sorted(pairs, key=lambda x: x[0])

def data(node):
    chunks = ['data_', node.name, '\n']
    for (savename, saveframe) in sortByFirst(node.saves.iteritems()):
        chunks.extend(save(savename, saveframe))
    return chunks

def identifier(key):
    return ['_', key]

def datum(key, val):
    chunks = ['    ']
    chunks.extend(identifier(key))
    chunks.append(' ')
    chunks.extend(value(val))
    chunks.append('\n')
    return chunks

def save(name, node):
    chunks = ['\n  save_', name, '\n\n']
    for (key, val) in sortByFirst(node.datums.iteritems()):
        chunks.extend(datum(key, val))
    for myloop in node.loops:
        chunks.extend(loop(myloop))
    chunks.append('\n  save_\n')
    return chunks

SPECIALS = set('"\\')
def escapeVal(val):
    newVal = []
    for c in val:
        if c in SPECIALS:
            newVal.append('\\')
        newVal.append(c)
    return ''.join(newVal)

def value(val):
    return ['"', escapeVal(val), '"']

def loop(node):
    chunks = ['    ', 'loop_', '\n']
    for key in node.keys:
        chunks.append('      ')
        chunks.extend(identifier(key))
        chunks.append('\n')
    for row in node.rows:
        chunks.append('      ')
        for val in row:
            chunks.extend(value(val))
            chunks.append(' ')  # oops, what about the last iteration?
        chunks.append('\n')
    chunks.append('    stop_\n')
    return chunks


def unparse(node):
    if type(node) != m.Data:
        raise TypeError(('unable to star-unparse value', node))
    chunks = data(node)
    return ''.join(chunks)
