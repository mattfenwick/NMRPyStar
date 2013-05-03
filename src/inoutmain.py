'''
Created on May 2, 2013

@author: mattf
'''
import patcher.trial as pt
import sys


try:
    action = sys.argv[1]
    if action == 'star2xez':
        hncopath, nhsqcpath, starpath = sys.argv[2:]    
        paths = {'hnco': hncopath, 'nhsqc': nhsqcpath}
        pt.star_to_xez(paths, starpath)
    elif action == 'xez2star':
        hncopath, nhsqcpath, starpath = sys.argv[2:]    
        paths = {'hnco': hncopath, 'nhsqc': nhsqcpath}
        pt.xez_to_star(paths, starpath)
    elif action == 'star2xeztag':
        tag, nhsqc, star = sys.argv[2:]
        pt.star_filter_hsqc_to_xez(nhsqc, star, tag)
    else:
        print 'error: invalid action.  valid actions are star2xez, xez2star, and star2xeztag'
except Exception as e:
    print 'error: ', e
    print 'correct usage is:  <program> <action> <hncopath> <nhsqcpath> <starpath>'
    