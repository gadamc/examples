#!/usr/bin/env python

from couchdbkit import Server, Database
import sys

def onIgnoreList(key):
  ignoreList = ['_id', '_rev',
                 'author',
                 'content',
                 'date_filed',
                 'type',
                  'bolometer'
                 ]
  return key in ignoreList 

s = Server('https://edwdbik.fzk.de:6984')
db = s['bolohardwaremap']
vr = db.view('map/bolometer', include_docs = True, reduce = False)

width = 20

for row in vr:
  doc = row['doc']
  print '  Bolometer :  ', doc['bolometer']  
  for key, value in doc.items():
    if onIgnoreList(key) is False:
      print ''.join([str(s).rjust(width) for s in [key, value]])

  go = ''
  while (go != 'y' and go != 'n'):
    go = raw_input('Get Next Record (y/n)?')
    
  if go == 'n':
    sys.exit(0)
  
  print '\n'

  

