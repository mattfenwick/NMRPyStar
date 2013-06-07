## NMRPyStar ##

A tool for parsing and unparsing NMR-Star files, the format used by the BMRB
for archival of NMR data.

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

 - how, when, and with what debugging information errors are reported
 
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



### General project organization ###

 - parser combinators.  General set of building blocks
   for constructing parsers
 
 - full NMR-Star:
 
   - grammar
   
   - tokenizer
 
 - simplified NMR-Star:  reduces rule duplication and 
   removes need for lookahead and backtracking.  Allows
   better error reporting and easier unparsing
   
   - grammar 
   
   - tokenizer
   
   - unparser

 - NMR-Star data model 

 - NMR-Star hierarchical parser
   input:  tokens
   output:  error or instance of NMR-Star data model
 
 - unit tests

 

### Contact information ###

Found a bug?  Need help figuring something out?  Want a new feature?  Feel free
to report anything using the github issue tracker, or email me directly at
mfenwick100 at gmail dot com
