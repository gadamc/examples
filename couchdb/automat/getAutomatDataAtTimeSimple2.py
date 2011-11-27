#!/usr/bin/env python

from couchdbkit import Server, Database
import sys, math, os, datetime, time, copy

s = Server('https://edwdbik.fzk.de:6984')
db = s['automat']
  
cryoKey = 'T_Bolo'

eventTime = 1322161265.017829
  
#set how far into the past you want to look
startTime = eventTime - 30
      
#get view results from the database
vr = db.view('data/bypctime',  startkey=eventTime, endkey=startTime,  include_docs=True, descending=True)
  
#search for the first value we find, which will be the value most recently measured relative to our eventTime
for row in vr:  
  doc = row['doc']
  if cryoKey in doc:
    print doc[cryoKey]
    #print doc['date']
    #print doc['utctime']
    break
  
  
