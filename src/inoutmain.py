'''
Created on May 2, 2013

@author: mattf
'''
import patcher.trial as pt
import sys


try:
    action, hncopath, nhsqcpath, starpath = sys.argv[1:]    
    paths = {'hnco': hncopath, 'nhsqc': nhsqcpath}
    if action == 'star2xez':
        pt.star_to_xez(paths, starpath)
    elif action == 'xez2star':
        pt.xez_to_star(paths, starpath)
    else:
        print 'error: invalid action.  valid actions are star2xez and xez2star'
except Exception as e:
    print 'error: ', e
    print 'correct usage is:  <program> <action> <hncopath> <nhsqcpath> <starpath>'
    