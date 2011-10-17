#!/usr/bin/env python
# -*- coding: utf-8 -*-

from couchdbkit import Server, Database
import sys, math, datetime


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
    5. list all of the dates when bolometer configurations have been uploaded to the database

    Here are the examples for each one
    1) ./boloMapQueryDb.py boloinfo ID6R <optional date in formay year,month,day - "2011,10,01">
    
    2) ./boloMapQueryDb.py listfields
    
    3) ./boloMapQueryDb.py repartition_type sc <optional date in formay year,month,day - "2011,10,01">
    
    4) ./boloMapQueryDb.py listbolos
    
    5) ./boloMapQueryDb.py listdates
    
  '''
  s = Server('https://edwdbik.fzk.de:6984')
  db = s['bolohardwaremap']

  if len(argv) == 0:
    print 'You need to supply some arguments'
    help(main)
    return 
  
  arg1 = argv[0]
  if len(argv) > 1:
    arg2 = formatvalue(argv[1])
  
  date = datetime.date(datetime.MINYEAR, 1, 1)

  if len(argv) > 2:
    date = datetime.date(formatvalue(argv[2].split(',')[0].strip(' ')), formatvalue(argv[2].split(',')[1].strip(' ')), formatvalue(argv[2].split(',')[2].strip(' ')))


  if arg1 == 'boloinfo':
    vr = db.view('map/bolometer', reduce = False, descending = True)
  
    width = 20
    for row in vr:
      if arg2 == row['key']:
        doc = db.get(row['id'])
        docdate = datetime.date(doc['date_valid']['year'], doc['date_valid']['month'], doc['date_valid']['day'])
        if docdate >= date:
          print '\n'
          print 'Date Valid (Year/Month/Day)', doc['date_valid']['year'], doc['date_valid']['month'], doc['date_valid']['day']
          print 'Channels', ''.join(str(' '+i) for i in doc['channels'])
          #for i in range(len(doc['channels'])):
          #  print doc['channels'][i]
                       
          for key, value in doc.items():
            if onIgnoreList(key) is False:
              print ''.join([str(s).rjust(width) for s in [key, value]])
  
  

  elif arg1 == 'listfields':
    vr = db.view('map/keys', group = True)
    for row in vr:
      if row['key'] != '_id' and row['key'] != '_rev':
       print row['key']
  

  elif arg1 == 'listbolos':
    vr = db.view('map/bolometer', group = True)
    for row in vr:
      print row['key']


  elif arg1 == 'listdates':
    vr = db.view('map/date_valid', group = True)
    for row in vr:
      print row['key']



  else: 
    vr = db.view('map/bolometer', reduce = False)
  
    for row in vr:
      #print row['id']
      doc = db.get(row['id'])
      if doc.has_key(arg1):
        #print doc[key]
        docdate = datetime.date(doc['date_valid']['year'], doc['date_valid']['month'], doc['date_valid']['day'])
        if doc[arg1] == arg2 and docdate >= date:
          print 'bolometer:', doc['bolometer'], 'channels:', doc['channels'], 'date_valid', doc['date_valid']
      

if __name__ == '__main__':
  main(*sys.argv[1:])
