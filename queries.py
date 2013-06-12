'''
@author: matt
'''
import examples


star = examples.parseFile()[2]

saveShifts = star.saves['assigned_chem_shift_list_1']

loopShifts = saveShifts.loops[1]

for ix in range(len(loopShifts.rows)):
    row = loopShifts.getRowAsDict(ix)
    print 'chemical shift: ', \
          row['Atom_chem_shift.Seq_ID'], \
          row['Atom_chem_shift.Comp_ID'], \
          row['Atom_chem_shift.Atom_ID'], \
          row['Atom_chem_shift.Val']
