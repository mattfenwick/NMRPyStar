## NMRPyStar ##

A tool for parsing and unparsing NMR-Star files.

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