from .. import parser
import json
import urllib2
import numpy
import sys


def parseUrl(url):
    page = urllib2.urlopen(url)
    inputStr = page.read()
    page.close()
    return parser.parse_nmrstar_ast(inputStr)

def parseFile(path):
    with open(path, 'r') as my_file:
        return parser.parse_nmrstar_ast(my_file.read())
    
def getChemicalShifts(dataBlock, saveName='assigned_chem_shift_list_1'):
    saveShifts = dataBlock.saves[saveName]
    loopShifts = saveShifts.loops['Atom_chem_shift']
    
    shifts = {}
    for ix in range(len(loopShifts.rows)):
        row = loopShifts.getRowAsDict(ix)
        key = (row['Comp_ID'], row['Atom_ID'])
        if not key in shifts:
            shifts[key] = []
        shifts[key].append(float(row['Val']))
    return shifts

def query(model):
    shifts = getChemicalShifts(model)
    many = [(k, (len(v), numpy.std(v))) for (k, v) in shifts.items()]
    devs = filter(lambda x: x[1][0] > 1, sorted(many, key=lambda x: x[0]))
    for result in sorted(devs, key=lambda x: (x[0][1], x[1][1])):
        print result
    return None

def from_url():
    result = parseUrl('http://rest.bmrb.wisc.edu/bmrb/NMR-STAR3/18504')
    if result.status == 'success':
        return query(result.value)

def from_file():
    result = parseFile('examples/star18504.txt')
    if result.status == 'success':
        return query(result.value)

def from_stdin():
    result = parser.parse_nmrstar_ast(sys.stdin.read())
    if result.status == 'success':
        return query(result.value)

mode = sys.argv[1]
if mode == 'url':
    from_url()
elif mode == 'file':
    from_file()
elif mode == 'stdin':
    from_stdin()
else:
    raise ValueError('invalid mode -- %s' % mode)

