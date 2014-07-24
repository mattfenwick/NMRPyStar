## NMRPyStar ##

A library for parsing data in NMR-Star format, used
by the BMRB for NMR (Nuclear Magnetic Resonance) data
archival.

This is an open source project under the MIT license; 
feel free to use the code in any way that helps you get
some awesome science done!
 


### Installation ###

The easiest way to install NMRPyStar is using pip:

    $ pip install nmrpystar

If you don't have pip or easy_install, you can download the package
manually from [the pypi page](https://pypi.python.org/pypi/NMRPyStar).



### Quick Start ###

You've already got NMRPyStar installed and importable?  Great!
It's easy to start parsing NMR-Star files:

    import nmrpystar
    
    myString = ...read a file/url/stdin/string...
    
    parsed = nmrpystar.parse(myString)
    if parsed.status == 'success':
        print 'it worked!!  ', parsed.value
    else:
        print 'uh-oh, there was a problem with the string I gave it ... ', parsed



### Python version ###

This library was created for use with Python2.7.  Although it may work
with other Python versions, I haven't tried that.



### Motivation ###

Why is this project necessary?  After all, many people have already written
working NMR-Star parsers.

However, not all parsers -- even of the same format -- are identical.  Here
are some of the important characteristics that determine how nice, easy, etc.
it is to use a parser:

 - what language the parser actually accepts.  Some NMR-Star parsers accept
   malformed files, or fail on perfectly acceptable NMR-Star files.  
   
   This project aims to: 1) accurately parse all valid NMR-Star input, 
   and 2) accurately recognize and report all invalid NMR-Star input.
   
   This is done using a grammar to define the syntax, from which a parser is
   generated.  Although the grammar is believed to be correct, it's always
   possible that there are mistakes -- feel free to contact me if you find one, 
   I will be happy to make any corrections.

 - what the parse result is.  What access does the user have to the parsed result?
   What, if any, information is missing from the result?
   
   The output of this parser is a parse tree representing the structure of the
   input, including data blocks, save frames, loops, and key-value pairs.  The
   parse tree is composed of Python objects, against which queries can be easily
   written to extract the required data.

 - error reporting:  how, when, and with what context information
 
   Accurately reporting where and why input is malformed is a key aspect of a
   parser that's nice to use.  Arguably, error reporting should be part of a 
   format specification -- this parser does its best to report errors, but it's
   not always clear how an error should be reported.  Suggestions welcome!

 - how the parser is used -- is it a stand-alone tool?  Can it be imported
   as a library?
   
   This parser is designed to be used as a library -- simply import it, hand it
   your NMR-Star input, and set it loose!
 
 - modularity and flexibility -- can the parser operate on stdin and stdout? Can
   it parse content pulled from a web page?  Can it parse multiple files at once?
   
   This parser doesn't know anything about files, urls, or I/O streams -- any
   way you use to read in your data and hand it to the parser is fine.  This means
   that it's easy to parse files from the BMRB's web interface -- just use the
   `urllib2` library to grab a web page, and hand the contents to the parser!
   
 - licensing, cost, restrictions.
 
   This project is 100% open-source under the MIT license.  This means that you
   may use it in any way you wish, including reading, modifying, and sharing
   the code.



## NMR-Star Grammar ##

Derived from the Spaddaccini and Hall papers describing the Star format, 
and with thanks to Dmitri Maziuk for his pointers.

Tokens:

    newline    :=  '\n'   |  '\r'

    blank      :=  ' '    |  '\t'

    space      :=  blank  |  newline

    stop       :=  /stop_/i

    saveclose  :=  /save_/i

    loop       :=  /loop_/i

    dataopen   :=  /data_/i  (not space)(+)

    saveopen   :=  /save_/i  (not space)(+)
    
    identifier :=  '_'  (not space)(+)

    unquoted   :=  (not special)  (not space)(*)
      where
        special    :=  '"'  |  '#'  |  '_'  |  '\''  |  space

    scstring   :=  ns  (not ns)(*)  ns
      where
        ns     :=  newline  ';'

    sqstring   :=  '\''  ( nonEndingSq  |  bodyChar )(*)  '\''
      where
        nonEndingSq  :=  '\''  (not space)
        bodyChar     :=  (not ( '\''  |  newline ) )

    dqstring   :=  '"'  ( nonEndingDq  |  bodyChar )(*)  '"'
      where
        nonEndingDq  :=  '"'  (not space)
        bodyChar     :=  (not ( '"'  |  newline ) )

    value      :=  sqstring  |  dqstring  |  scstring  |  unquoted

    comment    :=  '#'  (not newline)(*)

    whitespace :=  space(+)

In addition, any amount of whitespace and comments is allowed before
any token (the tokens are: `stop`, `saveopen`, `saveclose`,
`loop`, `dataopen`, `identifier`, and `value`), except that unquoted
values may not be preceded by newlines if they start with semicolons.

Also, reserved words -- `stop_`, `save_`, `loop_`, `save_[^ \n\t\r]+`,
`data_[^ \n\t\r]+` -- take precedence over unquoted values, meaning 
that `stop_` cannot be an unquoted value.

Context-free grammar.  Note that hierarchical rules' first letters 
are capitalized, while token names are all lowercase:

    NMRStar  :=   Data 
        
    Data     :=   dataopen  Save(*)
        
    Save     :=   saveopen  Datum(*)  Loop(*)  saveclose
        
    Datum    :=   identifier  value
        
    Loop     :=   loop  identifier(*)  value(*)  stop


Context-sensitive rules:

 - no repeated identifiers in loops
 - no repeated identifiers in save frames
 - no duplicate save frame names
 - number of values in a loop must be an integer multiple
   of the number of keys



### Error conditions ###

 - tokenization:
   - unclosed single-quote string
   - newline in single-quote strings
   - unclosed double-quote string
   - newline in double-quote strings
   - unclosed semicolon-delimited string
 
 - nmrstar 
   - data block must be successfully parsed
   - entire string must be successfully parsed
 
 - data block:
   - invalid content:  loop or key/val

 - save frame:
   - unclosed
   - invalid content
   - duplicate keys
   - key/value pairs after loop
 
 - loop:
   - unclosed
   - invalid content
   - number of values is not an integer multiple of number of keys
   - duplicate keys
 
 - datum (key-val pair):
   - missing value



### Reference ###

Parser Combinators: a Practical Application for Generating Parsers for NMR Data 
 by Fenwick et al, Proceedings of the ITNG, 2013.

 

### Contact information ###

Found a bug?  Need help figuring something out?  Want a new feature?  Feel free
to report anything using the github issue tracker, or email me directly at
mfenwick100 at gmail dot com
