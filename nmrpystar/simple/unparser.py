from .. import model
from . import tokenizer


# see http://stackoverflow.com/questions/2158395/flatten-an-irregular-list-of-lists-in-python
#   for a possibly better solution to nested list flattening
#
# issues:
#   - whether " and \ can go in save/data names and identifier names (yes)
#   - whether whitespace can be in data block, save frame, and identifier names (no)

def sortByFirst(pairs):
    return sorted(pairs, key=lambda x: x[0])


def data(node):
    chunks = ['data_', checkName(node.name), '\n\n']
    for (savename, saveframe) in sortByFirst(node.saves.iteritems()):
        chunks.extend(save(savename, saveframe))
        chunks.append('\n')
    return chunks


def checkName(key):
    if set(key).intersection(tokenizer._WHITESPACE) != set([]):
        raise ValueError("identifiers may not contain whitespace")
    return key


def identifier(key):
    return ['_', checkName(key)]


def datum(key, val):
    chunks = ['    ']
    chunks.extend(identifier(key))
    chunks.append(' ')
    chunks.extend(value(val))
    chunks.append('\n')
    return chunks


def save(name, node):
    chunks = ['  save_', checkName(name), '\n\n']
    for (key, val) in sortByFirst(node.datums.iteritems()):
        chunks.extend(datum(key, val))
    chunks.append('\n')  # <-- extra newline when save frame is empty !!!
    for myloop in node.loops:
        chunks.extend(loop(myloop))
        chunks.append('\n')
    chunks.append('  save_\n')
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
    if type(node) != model.Data:
        raise TypeError(('unable to star-unparse value', node))
    chunks = data(node)
    return ''.join(chunks)
