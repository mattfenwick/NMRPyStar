## Simple Grammar ##

This grammar reduces rule duplication and removes need for lookahead and backtracking.
The semantic expressiveness of the format is unchanged.
It is *not* compatible with the NMR-STAR format.  Its goals are to:

 1. simplify the specification.  This helps implementors to:
   - implement the entire specification
   - test the entire implementation
 2. allow simple and accurate error reporting 
 3. simplify unparsing
 4. eliminate corner cases requiring special handling


### Specific NMR-STAR syntax issues addressed ###

 - inconsistent whitespace/comment allowances:
   - space or tab is required before some types of values
   - newline is required before semicolon-delimited values
   - arbitrary whitespace/comments may appear before other tokens
 
 - ambiguities requiring lookahead to solve:
   - keyword vs unquoted:  
     - keyword: `stop_`
     - unquoted value: `stop_123`
   - semicolon-delimited vs. unquoted:  
     - semicolon-delimited: `;abc\n;`
     - unquoted value: `;abc`
   - value-ending quote (see next issue)
 
 - complicated rules for when and how delimiters may appear inside 
   delimited values:
   - single-quote strings: end `'` must be followed by whitespace or EOF:
     - yes: `'a'b'`
     - no: `'a' b'`
   - double-quote strings: end `"` must be followed by whitespace or EOF:
     - yes: `"a"b"`
     - no: `"a" b"`
   - semicolon-delimited strings:  `;` can not appear at the beginning of a line
     within the string:
     - yes: `\n;a\nb;\n;`
     - no: `\n;a\n;\n;`
 
 - multiple ways to denote equivalent values:
   - unquoted:  `abc`
   - single-quoted: `'abc'`
   - double-quoted: `"abc"`
   - semicolon-delimited: `\n;abc\n;`
 
 - arbitary restrictions on what characters can be used where:
   - no newlines in single-quote values
   - no newlines in double-quote values
 
 - emergent corner cases
   - no empty unquoted values
   - no unquoted values that match a reserved word
   - no unquoted values starting with a special character
   - no unquoted values containing whitespace
 
 - case-insensitive keywords, but case-sensitive values
   - `stop_` and `StoP_` are treated as the same token, although they are different
   - `abc` and `ABC` are treated as different tokens


### How does this grammar solve the above problems? ###

 - uniform whitespace/comment allowances:  any amount of whitespace
   and comments may appear before any token
 
 - no unquoted values
   - solves unquoted/keyword ambiguity
   - solves unquoted/semicolon-delimited ambiguity
   - solves unquoted corner cases
 
 - all values are double-quoted
   - solves rule equivalence
 
 - newlines (and all other characters) are allowed in values
   - solves arbitrary restrictions
 
 - escape sequences are supported within values:  use `\"` to always denote 
   a non-terminating double-quote, `\\` to denote a non-escaping slash.  Now
   `"` always means open value or close value
   - solves delimiters inside delimited values
 
 - permissible first characters of tokens are distinct sets:  identifiers
   start with `_`, values with `"`, and keywords with `[a-zA-Z]`
   - allows token type prediction based on first character of token: no
     backtracking or lookahead is required to correctly tokenize
 
 - case is always significant
   - keywords are all lowercase -- one way to write each keyword
   - no difference between keywords and values with respect to case treatment


### Grammar ###

Tokens:

    newline    :=  '\n'  |  '\r'
    
    space      :=  '\t'  |  ' '

    comment    :=  '#'  (not newline)(*)

    whitespace :=  ( newline  |  space )(+)

    stop       :=  "stop_"

    saveclose  :=  "save_"

    loop       :=  "loop_"

    dataopen   :=  "data_"  (not whitespace)(+)

    saveopen   :=  "save_"  (not whitespace)(+)

    identifier :=  '_'  (not whitespace)(+)
    
    value      :=  '"'  ( simplechar  |  escape )(*)  '"'
      where
        simplechar  :=  (not  ( '"'  |  '\\' ))
        escape      :=  '\\'  ( '"'  |  '\\' )

Whitespace and comments may appear in any amount before any token.  The tokens
are: `stop`, `saveclose`, `saveopen`, `loop`, `dataopen`, `identifier`, and `value`.

Context-free grammar:

    NMRStar  :=   Data 
        
    Data     :=   dataopen  Save(*)
        
    Save     :=   saveopen  Datum(*)  Loop(*)  saveclose
        
    Datum    :=   identifier  value
        
    Loop     :=   loop  identifier(*)  value(*)  stop
