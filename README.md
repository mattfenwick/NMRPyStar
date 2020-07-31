## NMRPyStar ##

A library for parsing data in NMR-STAR format, used
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



### Uninstallation ###

If it was installed with `pip`, it can be easily uninstalled:

    $ pip uninstall nmrpystar



### Quick Start ###


It's easy to start parsing NMR-STAR files:

    import nmrpystar
    
    myString = ...read a file/url/stdin/string...
    
    parsed = nmrpystar.parse(myString)
    if parsed.status == 'success':
        print 'it worked!!  ', parsed.value
    else:
        print 'uh-oh, there was a problem with the string I gave it ... ', parsed

Or try out one of the examples:

    ./integration-tests.sh


### Running the tests

```bash
python3 -m unittest
```


### Python version ###

This library was created for use with Python3.  I'm working on making it compatible
with Python2 as well.



### Motivation ###

Why is this project necessary?  After all, many people have already written
working NMR-STAR parsers.

However, not all parsers of the same format are identical.  Here are some
important characteristics of parsers:

 - what language the parser actually accepts.  Some parsers are more lenient,
   accepting some malformed input; others may reject perfectly valid input.  
   
   This project aims to: 1) accurately parse all valid NMR-STAR input, 
   and 2) accurately recognize and report all invalid NMR-STAR input.
   
 - what the parse result is.  What access does the user have to the parsed result?
   What information is included in the result?
   
   The output of this parser is a parse tree representing the structure of the
   input, including data blocks, save frames, loops, and key-value pairs.  The
   parse tree is composed of Python objects, against which queries can be easily
   written to extract the required data.

 - error reporting:  how, when, and with what context information
 
   Accurately reporting where and why makes it easier to locate and fix errors.

   Arguably, error reporting should be part of a 
   format specification -- this parser does its best to report errors, but it's
   not always clear how an error should be reported.  Suggestions welcome!

 - how the parser is used -- is it a stand-alone tool?  Can it be imported
   as a library?
   
   This parser is designed to be used as a library -- simply import it, hand it
   your NMR-STAR input, and set it loose!
 
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



## NMR-STAR Grammar ##


Derived from the Spaddaccini and Hall papers describing the Star format, 
and with thanks to Dmitri Maziuk for his pointers.

The following grammar is used to generate a parser.  Although I believe that 
it is correct, if you find a mistake please contact me, I am always happy to 
make corrections.

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


Additional constraints for STAR AST:

 - Loops
   - no duplicate keys
   - number of values must be integer multiple of the number of keys
 - Save frames
   - no duplicate keys
 - Data
   - no duplicate save frame names

Additional constraints for NMRSTAR AST:

 - Loops: 
   - prefix of all keys must be identical
 - Save frames
   - prefix of all keys must be identical
   - have an `_<prefix>.Sf_framecode` key, value matches the save frame name
   - have an `_<prefix>.Sf_category` key, value is a link to the NMR-STAR data dictionary
   - no duplicate loops, based on the loop prefixes

Questionable (as in not sure if these are actually enforced) rules:
 - Save frames
   - if there's a `_<prefix>.ID` key, it must appear in each loop table within the
     save frame, under the key `_<loop-prefix>.<prefix>_ID` and the same value
 - General
   - `_<prefix>.Entry_ID` must appear in every Save frame and every loop, with the same value



### Reference ###

Parser Combinators: a Practical Application for Generating Parsers for NMR Data 
 by Fenwick et al, Proceedings of the ITNG, 2013.

 

### Contact information ###

Found a bug?  Need help figuring something out?  Want a new feature?  Feel free
to report anything using the github issue tracker, or email me directly at
mfenwick100 at gmail dot com

### How to cut a release

 - update version strings
 - `python3 -m pip install --user --upgrade setuptools wheel`
 - `python3 setup.py sdist bdist_wheel`
 - `pip3 install twine`
 - `twine upload dist/*`
