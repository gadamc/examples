#!/usr/bin/env python

from couchdbkit import Server, Database
import sys, math, os, datetime, time, copy


  
s = Server('https://edwdbik.fzk.de:6984')
db = s['automat']
  
cryoKey = 'T_Bolo'


eventTime = datetime.datetime( 2011, 11, 24, 15, 23, 8, 230045)
#or, with POSIX time
#eventTime = datetime.datetime.utcfromtimestamp( 1322161265.017829  )
  
#set how far into the past you want to look
startTime = eventTime - datetime.timedelta(seconds = 30)
    
#we have to make an array for the startkey and endkey options... cumbersome programming.
skey = [startTime.year, startTime.month, startTime.day, startTime.hour, startTime.minute, startTime.second, startTime.microsecond]
evkey  = [eventTime.year, eventTime.month, eventTime.day, eventTime.hour, eventTime.minute, eventTime.second, eventTime.microsecond]
  
#get view results from the database
vr = db.view('data/bydate', endkey=skey, startkey=evkey, reduce=False, include_docs=True, descending=True)
  
#search for the first value we find, which will be the value most recently measured relative to our eventTime
for row in vr:  
  doc = row['doc']
  if cryoKey in doc:
    print doc[cryoKey], doc['date']
    break
  
  
  