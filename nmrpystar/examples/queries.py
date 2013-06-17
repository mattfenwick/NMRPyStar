
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
