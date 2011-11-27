#!/usr/bin/env python

from couchdbkit import Server, Database
import sys, math, os, datetime, time, copy

def listVars(s, db):
  #get list of ip addresses that hold data
  vr = db.view('data/byipaddress', group_level=1)

  ips = []
  #search for variable
  for row in vr:
    ips.append(row['key'])
  
  correctIp = 0
  for ip in ips: 
    print '   from IP address:', ip
    vr = db.view('data/byipaddress', reduce=False, key= ip, limit=1, include_docs=True, descending=True)
    doc = vr.first()['doc']
    for key in doc.iterkeys():
      print key

def badExit(thekey):
  sys.stderr.write('Couldn\'t find cryogenic variable: %s \n' % thekey)
  sys.exit(-1)
  
def main(*argv):
  '''
    Use this script to get the value of a particular cyrogenic variable at a particular time.
    
    usage: $> python getAutomateDataAtTime.py [variable name] [-pctime VAL optional]  [year] [month] [day] [hour] 
                                              [minute] [second] [microsecond (optional. = 0 by default)] [-method=name (optional, default is 'cn')]
                                              [-t=seconds (optional, default is 60 seconds)]
    
           $> python getAutomateDataAtTime.py list
                This will return a list of all cryogenic variables that are available according to the latest documents written 
                to the database. This doesn't necessarily mean that these cryogenic variables are available in all past data, but 
                that is probably a reasonable assumption since the cryogenic data server does not change often.
           
    The time is always UTC time. 
    
    [optional]
    -pctime [number]    Instead of passing in the year/month/day/hour/minutes/second/microsecond, you can pass in the PC time (which is)
    
    methods:
    -method=bn
          bn == "both neighbors". this will return the value of the cryogenic variable at both neighboring times
    -method=ex
          ex == 'extrapolate'
    -method=en
          en == "early neighbor". This returns the neighbor value measured prior to the time you provide     
    -method=ln
          ln == "late neighbor". This returns the neighbor value measured after the time you provide
    -method=cn
          cn == "closest neighbor". This returns the neighbor value thas was measured closest to time you provide
                
    time threshold:
      -t=seconds.   If the time you choose is further away than some time 'seconds' from the nearest measurement, this function will return a message to stderr and nothing to stdout
        
  '''

  
  s = Server('https://edwdbik.fzk.de:6984')
  db = s['automat']
  
  if argv[0] == 'list':
    listVars(s,db)
    return
  
  cryoKey = argv[0]
  
  #build the eventTime from the arguments
  eventTime = 0
  if argv[1] == '-pctime':
    eventTime = datetime.utcfromtimestamp(float(argv[2]))
  else:
    eventTime = datetime.datetime( int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4]), int(argv[5]), int(argv[6]) )
    if len(argv) >= 8:
      eventTime += datetime.timedelta(microseconds=float(argv[7]))
  
  #step back through the arguments to see if the user wants specific options
  global theMethod, timeThreshold
  theMethod = 'en'
  timeThreshold = 60
  def searchBack(*argv):
    global theMethod, timeThreshold
    
    lastArg = argv[len(argv)-1]
    if lastArg.startswith('-t'):
      timeThreshold =  float(lastArg.split('=')[1])
    elif lastArg.startswith('-method'):
      theMethod = lastArg.split('=')[1]
    else:
      #there are no more args to look at
      return
    
    newArgs = copy.deepcopy(argv[ : len(argv)-1])
    if len(newArgs) > 0: searchBack(*newArgs)
  
  #
  searchBack(*argv)
    
  #determine the range of times over which we'll query the database
  startTime = eventTime - datetime.timedelta(seconds=timeThreshold)
  endTime = eventTime + datetime.timedelta(seconds=timeThreshold)
    
  skey = [startTime.year, startTime.month, startTime.day, startTime.hour, startTime.minute, startTime.second, startTime.microsecond]
  evkey  = [eventTime.year, eventTime.month, eventTime.day, eventTime.hour, eventTime.minute, eventTime.second, eventTime.microsecond]
  ekey = [endTime.year, endTime.month, endTime.day, endTime.hour, endTime.minute, endTime.second, endTime.microsecond]
  
  
  start_vr = db.view('data/bydate', endkey=skey, startkey=evkey, reduce=False, include_docs=True, descending=True)
  end_vr = db.view('data/bydate', startkey=evkey, endkey=ekey, reduce=False, include_docs=True, descending=False)
  
  #define a helpful functions to return the first value it finds in a ViewReturn object
  def returnFirstVal(vr):
    for row in vr:  
      doc = row['doc']
      if cryoKey in doc:
        return doc[cryoKey], doc['date']
    return -1,-1
  
  
  
  if theMethod == 'en':  
    theVal, theTime = returnFirstVal(start_vr) #since descending=True was passed into the view request, this loop 
                                    #can quit as soon as the variable is found
    if theVal == -1: badExit(cryoKey)
    else: 
      print theVal
      
  
  elif theMethod == 'ln':
    theVal, theTime = returnFirstVal(end_vr)  #since descending=False was passed into the view request, this loop 
                          #can quit as soon as the variable is found
    if theVal == -1: badExit(cryoKey)
    else: 
      print theVal    
  
  
  elif theMethod == 'bn':
    earlyVal, earlyTime =  returnFirstVal(start_vr)
    lateVal, lateTime =  returnFirstVal(end_vr)
    if earlyVal == -1 and lateVal == -1: badExit(cryoKey)
    else: print earlyVal, lateVal
    
      
  elif theMethod == 'cn':
    earlyVal, earlyTime =  returnFirstVal(start_vr)
    lateVal, lateTime =  returnFirstVal(end_vr)

    if earlyVal == -1 and lateVal != -1:
      print lateVal, lateTime
    if lateVal == -1 and earlyVal != -1:
      print earlyVal, earlyTime
    if earlyVal == -1 and lateVal == -1: badExit(cryoKey)
      
    earlyDatTime = datetime.datetime(**earlyTime)
    lateDatTime = datetime.datetime(**lateTime)
    if eventTime - earlyDatTime > lateDatTime - eventTime: 
      print lateVal
    else: print earlyVal
  
    
  
  elif theMethod == 'ex':  
    earlyVal, earlyTime =  returnFirstVal(start_vr)
    lateVal, lateTime =  returnFirstVal(end_vr)

    if earlyVal == -1 and lateVal != -1:
      print lateVal
    if lateVal == -1 and earlyVal != -1:
      print earlyVal
    if earlyVal == -1 and lateVal == -1: badExit(cryoKey)
      
    earlyDatTime = datetime.datetime(**earlyTime)
    lateDatTime = datetime.datetime(**lateTime)
    
    
if __name__ == '__main__':
  main(*sys.argv[1:])