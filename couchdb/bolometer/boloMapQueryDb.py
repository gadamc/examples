#!/usr/bin/env python

from couchdbkit import Server, Database
import sys, math


def formatvalue(value):
  if (isinstance(value,str)):
    # #see if this string is really an int or a float
    if value.isdigit()==True: #int
      return int(value)
    else: #try a float
      try:
        if math.isnan(float(value))==False:
          return float(value)
      except:
        pass
    
    return value.strip('"') #strip off any quotations found in the value
  else:
    return value

def onIgnoreList(key):
  ignoreList = ['_id', '_rev',
                'author',
                'content',
                'date_filed',
                'type',
                'bolometer',
                'date_valid',
                'channels'
                ]
  return key in ignoreList 


def main(*argv):
  '''
    This script queries the edwdb database (on edwdbik.fzk.de) and returns information
    found in the Bolometer Hardware Map documents. You can do four things with this script.
    1. obtain the information for a particular Bolometer
    2. list the available fields to choose from in the bolometer map
    3. search for the bolometer that matches a particular field.
    4. list all of the available bolometer information in the database
    
    Here are the examples for each one
    1) ./boloMapQueryDb.py boloinfo ID6R
    
    2) ./boloMapQueryDb.py listfields
    
    3) ./boloMapQueryDb.py repartition_type sc
    
    4) ./boloMapQueryDb.py listbolos
    
    
  '''
  s = Server('http://edwdbik.fzk.de:5984')
  db = s['edwdb']

  if len(argv) == 0:
    print 'You need to supply some arguments'
    help(main)
    return 
  
  arg1 = argv[0]
  if len(argv) > 1:
    arg2 = formatvalue(argv[1])
  
  #print 'Searching Muon Veto DAQ Map for', arg1, '=', arg2

  
  if arg1 == 'boloinfo':
    vr = db.view('bolohardware/bbolopositionmap', reduce = False, descending = True)
  
    width = 20
    for row in vr:
      if arg2 == row['key'][3]:
        doc = db.get(row['id'])
        print '\n'
        print 'Date Valid (Year/Day/Month)', doc['date_valid']['year'], doc['date_valid']['day'], doc['date_valid']['month']
        print 'Channels'
        for i in range(len(doc['channels'])):
          print doc['channels'][i]
                       
        for key, value in doc.items():
          if onIgnoreList(key) is False:
            print ''.join([str(s).rjust(width) for s in [key, value]])
  
  

  elif arg1 == 'listfields':
    vr = db.view('bolohardware/bbolopositionmap', include_docs = True, reduce = False, limit = 1)
    doc = vr.first()['doc']
    for k,val in doc.items():
      if k != '_id' and k!= '_rev':
       print k
  

  elif arg1 == 'listbolos':
    vr = db.view('bolohardware/bbolopositionmap', group = True)
    for row in vr:
      print row['key'][3]



  else: 
    vr = db.view('bolohardware/bbolopositionmap', reduce = False)
  
    for row in vr:
      #print row['id']
      doc = db.get(row['id'])
      if doc.has_key(arg1):
        #print doc[key]
        if doc[arg1] == arg2:
          print 'bolometer:', doc['bolometer'], 'channels:', doc['channels'], 'date_valid', doc['date_valid']
      

if __name__ == '__main__':
  main(*sys.argv[1:])