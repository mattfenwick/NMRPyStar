from .. import fullparse as parser
import json
import urllib2
import numpy


def parseUrl(url):
    page = urllib2.urlopen(url)
    inputStr = page.read()
    page.close()
    return parser.parse(inputStr)
    
def getChemicalShifts(dataBlock, saveName='assigned_chem_shift_list_1'):
    saveShifts = dataBlock.saves[saveName]
    loopShifts = saveShifts.loops[1]
    
    shifts = {}
    for ix in range(len(loopShifts.rows)):
        row = loopShifts.getRowAsDict(ix)
        key = (row['Atom_chem_shift.Comp_ID'], row['Atom_chem_shift.Atom_ID'])
        if not key in shifts:
            shifts[key] = []
        shifts[key].append(float(row['Atom_chem_shift.Val']))
    return shifts

def run():
    model = parseUrl('http://rest.bmrb.wisc.edu/bmrb/NMR-STAR3/18504')
    if model.status == 'success':
        shifts = getChemicalShifts(model.value)
        many = [(k, (len(v), numpy.std(v))) for (k, v) in shifts.items()]
        devs = filter(lambda x: x[1][0] > 1, sorted(many, key=lambda x: x[0]))
        for result in sorted(devs, key=lambda x: (x[0][1], x[1][1])):
            print result
        return result

