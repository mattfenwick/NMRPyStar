

    XEasy     :=   Line1  DimLine(n)  PeakLine(*)
* the number of dimlines must match the number from Line1 *
    
    Line1     :=   '# Number of dimensions '  \d  '\n'
    
    DimLine   :=   '# INAME '  \d  ' '  \w  '\n'
    
    PeakLine  :=   Identifier  Shift(n)  Field(+)
* the number of shifts must match the number from Line1 *

    Identifier  :=  \d(+)
    
    Shift     :=   \d(+)  ( '.'  \d(*) )(?)
    
    Field     :=   (not \s)(+)
