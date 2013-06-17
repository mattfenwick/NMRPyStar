
def getChemicalShifts(dataBlock, saveShiftName='assigned_chem_shift_list_1'):
    saveShifts = dataBlock.saves[saveShiftName]
    loopShifts = saveShifts.loops[1]
    
    for ix in range(len(loopShifts.rows)):
        row = loopShifts.getRowAsDict(ix)
        print 'chemical shift: ', \
              row['Atom_chem_shift.Seq_ID'], \
              row['Atom_chem_shift.Comp_ID'], \
              row['Atom_chem_shift.Atom_ID'], \
              row['Atom_chem_shift.Val']


def getKeyValuePairs(dataBlock):
    for (name, save) in dataBlock.saves.items():
        print 'starting save frame: ', name
        for (key, val) in save.datums.items():
            print '  key:', key, '  value:', val
        print '\n'
            