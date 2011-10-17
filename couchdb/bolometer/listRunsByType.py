#!/usr/bin/env python

from couchdbkit import Server, Database
import sys

def main(*argv):
  '''
    This script queries the edwdb database (on edwdbik.fzk.de) and returns the runs
    of a particular type. This script can also list the types of runs that are available
    
    Here are the examples for each one
    
    1) ./listRunsByType.py "calibration gamma"
    2) ./listRunsByType.py list
    
  '''
    
  s = Server('https://edwdbik.fzk.de:6984')
  db = s['datadb']
        
  if len(argv) == 0:
    print 'You need to supply an argument'
    help(main)
    return 
      
  arg1 = argv[0]
    
    
  if arg1 == 'list':
    vr = db.view('header/runcondition', group_level=1)
    print 'Run Types'
    for row in vr:
      print row['key'][0]
  else:
    print 'looking for runs of type', arg1
    vr = db.view('header/runcondition', endkey = [arg1,''], startkey = [arg1+'\ufff0', ''], group_level = 2, descending = True)
    
    for row in vr:
      print row['key'][1]
    
    
if __name__ == '__main__':
  main(*sys.argv[1:])
