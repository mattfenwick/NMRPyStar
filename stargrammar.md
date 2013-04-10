Hierarchical grammar.  Note that hierarchical rules' first letters are capitalized,
while token names are all lowercase:

    NMRStar  :=   Data 
        
    Data     :=   dataopen   Save(+)
        
    Save     :=   saveopen   ( Datum  |  Loop )(*)   saveclose
        
    Datum    :=   identifier  value
        
    Loop     :=   loop  identifier(*)  value(*)  stop


Tokens:

    newline    :=  '\n'   |  '\r'  |  '\f'

    blank      :=  ' '    |  '\t'

    space      :=  blank  |  newline

    special    :=  '"'    |  '#'   |  '_'  |  space

    stop       :=  "stop_"

    saveclose  :=  "save_"

    loop       :=  "loop_"

    comment    :=  '#'  (not newline)(*)

    dataopen   :=  "data_"  (not space)(+)

    saveopen   :=  "save_"  (not space)(+)

    identifier :=  '_'  (not space)(+)

    unquoted   :=  (not special)  (not space)(*)

    endsc      :=  newline  ';'

    scstring   :=  ';'  (not endsc)(*)  endsc

    sqstring   :=  '\''  (not '\'')(+)  '\''
    
    sqstring   :=  '\''  ( ('\'' (not space))  |  (not '\'') )(+)  '\''

    dqstring   :=  '"'  (not '"')(+)  '"'

    value      :=  sqstring  |  dqstring  |  scstring  |  unquoted

    whitespace :=  blank(+)

    newlines   :=  newline(+)

    token      :=  dataopen   |  saveopen  |  saveclose  |  
                   loop       |  stop      |  value      |  
                   whitespace |  newlines  |  comment    |  
                   identifier
