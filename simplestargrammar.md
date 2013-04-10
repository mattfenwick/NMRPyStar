Hierarchical grammar.  Note that hierarchical rules' first letters are capitalized,
while token names are all lowercase:

    NMRStar  :=   Data 
        
    Data     :=   dataopen   Save(+)
        
    Save     :=   saveopen   ( Datum  |  Loop )(*)   saveclose
        
    Datum    :=   identifier  value
        
    Loop     :=   loop  identifier(*)  value(*)  stop


Tokens:

    newline    :=  '\n'  |  '\r'  |  '\f'
    
    space      :=  '\t'  |  ' '

    whitespace :=  ( newline  |  space )(+)

    stop       :=  "stop_"

    saveclose  :=  "save_"

    loop       :=  "loop_"

    comment    :=  '#'  (not newline)(*)

    dataopen   :=  "data_"  (not whitespace)(+)

    saveopen   :=  "save_"  (not whitespace)(+)

    identifier :=  '_'  (not whitespace)(+)

    value      :=  '"'  ((not  '"') | '\\"')(*)  '"'

    token      :=  dataopen   |  saveopen  |  saveclose  |  
                   loop       |  stop      |  value      |  
                   whitespace |  comment   |  identifier
