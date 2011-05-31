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

def main(*argv):
  '''
    This script queries the edwdb database (on edwdbik.fzk.de) and returns information
    found in the Muon Veto DAQ Map documents. You can do three things with this script.
    1. obtain the information for a particular muon module
    2. list the available fields to choose from in the muon veto daq map
    3. search for the muon module that matches a particular field.
    
    Here are the examples for each one
    1) ./vetoDaqDb.py moduleinfo 3
    
    2) ./vetoDaqDb.py list
    
    3) ./vetoDaqDb.py "HV channel" 134
    
    
  '''
  s = Server('http://edwdbik.fzk.de:5984')
  db = s['edwdb']

  if len(argv) == 0:
    print 'You need to supply some arguments'
    help(main)
    return 
  
  key = argv[0]
  if len(argv) > 1:
    value = formatvalue(argv[1])
  
  #print 'Searching Muon Veto DAQ Map for', key, '=', value

  
  if key == 'moduleinfo':
    vr = db.view('muonveto/daqmap', reduce = False)
  
    for row in vr:
      if row['key'][3] == value:
        print '\n'
        doc = db.get(row['id'])
        for k,val in doc.items():
          if k != '_id' and k!= '_rev':
            print k, val
        print '\n'
  

  elif key == 'list':
    vr = db.view('muonveto/daqmap', include_docs = True, reduce = False, limit = 1)
    doc = vr.first()['doc']
    for k,val in doc.items():
      if k != '_id' and k!= '_rev':
       print k
  

  else: 
    vr = db.view('muonveto/daqmap', reduce = False)
  
    for row in vr:
      #print row['id']
      doc = db.get(row['id'])
      if doc.has_key(key):
        #print doc[key]
        if doc[key] == value:
          print 'module:', doc['muonmodule'], 'end:', doc['end'], 'date_valid', doc['date_valid']
      else:
        print 'Exiting. Muon Veto DAQ docs do not have the key', key
        return


if __name__ == '__main__':
  main(*sys.argv[1:])