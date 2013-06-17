### Simple Grammar ###

This grammar reduces rule duplication and removes need for lookahead and backtracking.
It is *not* compatible with the NMR-Star format.
This helps to eable better error reporting and easier unparsing.
The expressiveness of the format is unchanged.

Hierarchical grammar:

    NMRStar  :=   Data 
        
    Data     :=   dataopen   Save(+)
        
    Save     :=   saveopen   ( Datum  |  Loop )(*)   saveclose
        
    Datum    :=   identifier  value
        
    Loop     :=   loop  identifier(*)  value(*)  stop


Tokens:

    newline    :=  '\n'  |  '\r'
    
    space      :=  '\t'  |  ' '

    whitespace :=  ( newline  |  space )(+)

    stop       :=  "stop_"

    saveclose  :=  "save_"

    loop       :=  "loop_"

    comment    :=  '#'  (not newline)(*)

    dataopen   :=  "data_"  (not whitespace)(+)

    saveopen   :=  "save_"  (not whitespace)(+)

    identifier :=  '_'  (not whitespace)(+)
    
    simplechar :=  (not  ( '"'  |  '\\' ))
    
    escape     :=  '\\'  ( '"'  |  '\\' )

    value      :=  '"'  ( simplechar  |  escape )(*)  '"'

    token      :=  dataopen   |  saveopen  |  saveclose  |  
                   loop       |  stop      |  value      |  
                   whitespace |  comment   |  identifier
