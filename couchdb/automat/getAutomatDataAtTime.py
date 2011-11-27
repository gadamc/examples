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
    Use this script to return the value of a particular cyrogenic variable at a particular time.
    
    usage: $> python getAutomateDataAtTime.py [variable name] [-pctime VAL optional]  
                                        [year] [month] [day] [hour] 
                                        [minute] [second] [microsecond (optional. = 0 by default)] 
                                        [-method=name (optional, default is 'in')]
                                        [-t=seconds (optional, default is 60 seconds)]
                                        [-server=<address> (optional, 
                                                where address is 'http://dnsname:portNumber')]
                                        [-db=name (optional, default is 'automat')]
    
    
           examples: 
                    python getAutomatDataAtTime.py T_Speer 2011 10 27 0 10 10 0
                    python getAutomatDataAtTime.py T_Speer 2011 10 27 0 10 10 0 -method=bn
                    python getAutomatDataAtTime.py T_Bolo -pctime 1321101265.017829
                    python getAutomatDataAtTime.py T_Bolo -pctime 1321101265.017829 -t=1000 -method=cn

    
           $> python getAutomateDataAtTime.py list
                This will return a list of all cryogenic variables that are available according to the 
                latest documents writtento the database. This doesn't necessarily mean that these 
                cryogenic variables are available in all past data, but that is probably a reasonable
                assumption since the cryogenic data server does not change often.
           
    The time is always UTC time. 
    
    [optional]
    -pctime [number]    Instead of passing in the year/month/day/hour/minutes/second/microsecond, 
                        you can pass in the PC time (which is)
    
    methods:
    -method=bn
          bn == "both neighbors". this will return the value of the cryogenic variable at both 
                                  neighboring times
    -method=in
          in == 'interpolation'. This computes the interpolated value between neighboring measurements. 
                                 If this method fails because one of the nearby event times is 
                                 outside of range (set by the -t=seconds option), then the calculation 
                                 is redone using the -method=cn switch. 
    -method=en
          en == "early neighbor". This returns the neighbor value measured prior to the time you provide     
    -method=ln
          ln == "late neighbor". This returns the neighbor value measured after the time you provide
    -method=cn
          cn == "closest neighbor". This returns the neighbor value thas was measured closest to time you provide
                
    time threshold:
      -t=seconds.   Searches around your given event time by a range of +- seconds. If no data is found 
                    in this range, nothing is printed to stdout and an error message is printed to stderr
        
    select database server
      -server=address   Default: address = https://edwdbik.fzk.de:6984. If you're using a local CouchDB,
                        you probably want address = http://127.0.0.1:5984
    
    select database name
      -db=name          Default: automat. 
  '''

  cryoKey = argv[0]
  
  #build the eventTime from the arguments
  eventTime = 0
  if argv[1] == '-pctime':
    eventTime = datetime.datetime.utcfromtimestamp(float(argv[2]))
  else:
    eventTime = datetime.datetime( int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4]), int(argv[5]), int(argv[6]) )
    if len(argv) >= 8:
      eventTime += datetime.timedelta(microseconds=float(argv[7]))
  
  #step back through the arguments to see if the user wants specific options
  global theMethod, timeThreshold, servName, dbName
  theMethod = 'en'
  timeThreshold = 60
  servName = 'https://edwdbik.fzk.de:6984'
  dbName = 'automat'
  def searchBack(*argv):
    global theMethod, timeThreshold, servName, dbName
    
    lastArg = argv[len(argv)-1]
    if lastArg.startswith('-t'):
      timeThreshold =  float(lastArg.split('=')[1])
    elif lastArg.startswith('-method'):
      theMethod = lastArg.split('=')[1]
    elif lastArg.startswith('-server'):
      servName = lastArg.split('=')[1]
    elif lastArg.startswith('-db'):
      dbName = lastArg.split('=')[1]
    else:
      #there are no more recognized args to look at
      return
    
    newArgs = copy.deepcopy(argv[ : len(argv)-1])
    if len(newArgs) > 0: searchBack(*newArgs)
  
  #
  searchBack(*argv)
  
  s = Server(servName)
  db = s[dbName]
    
  if argv[0] == 'list':
    listVars(s,db)
    return
    
  
  #determine the range of times over which we'll query the database
  startTime = eventTime - datetime.timedelta(seconds=timeThreshold)
  endTime = eventTime + datetime.timedelta(seconds=timeThreshold)
    
  #we break up the query of the database into two queries with the event time at the boundary
  skey = [startTime.year, startTime.month, startTime.day, startTime.hour, startTime.minute, startTime.second, startTime.microsecond]
  evkey  = [eventTime.year, eventTime.month, eventTime.day, eventTime.hour, eventTime.minute, eventTime.second, eventTime.microsecond]
  ekey = [endTime.year, endTime.month, endTime.day, endTime.hour, endTime.minute, endTime.second, endTime.microsecond]
  
  #get the two view results from the database
  start_vr = db.view('data/bydate', endkey=skey, startkey=evkey, reduce=False, include_docs=True, descending=True)
  end_vr = db.view('data/bydate', startkey=evkey, endkey=ekey, reduce=False, include_docs=True, descending=False)
  
  #define a helpful function to return the first value it finds in a ViewReturn object
  def returnFirstVal(vr):
    for row in vr:  
      doc = row['doc']
      if cryoKey in doc:
        return doc[cryoKey], doc['date']
    return -1,-1
  
  
  #return the value appropriate for the chosen method
  if theMethod == 'en':  
    theVal, theTime = returnFirstVal(start_vr) 
    if theVal == -1: badExit(cryoKey)
    else: return theVal
      
  
  elif theMethod == 'ln':
    theVal, theTime = returnFirstVal(end_vr)  
    if theVal == -1: badExit(cryoKey)
    else: return theVal    
  
  
  elif theMethod == 'bn':
    earlyVal, earlyTime =  returnFirstVal(start_vr)
    lateVal, lateTime =  returnFirstVal(end_vr)
    if earlyVal == -1 and lateVal == -1: badExit(cryoKey)
    else: return earlyVal, lateVal
    
      
  elif theMethod == 'cn':
    earlyVal, earlyTime =  returnFirstVal(start_vr)
    lateVal, lateTime =  returnFirstVal(end_vr)

    if earlyVal == -1 and lateVal != -1:
      return lateVal
    if lateVal == -1 and earlyVal != -1:
      return earlyVal
    if earlyVal == -1 and lateVal == -1: badExit(cryoKey)
      
    earlyDatTime = datetime.datetime(**earlyTime)
    lateDatTime = datetime.datetime(**lateTime)
    if eventTime - earlyDatTime > lateDatTime - eventTime: return lateVal
    else: return earlyVal
  
    
  
  elif theMethod == 'in':  
    earlyVal, earlyTime =  returnFirstVal(start_vr)
    lateVal, lateTime =  returnFirstVal(end_vr)

    if earlyVal == -1 and lateVal != -1:
      return lateVal
    if lateVal == -1 and earlyVal != -1:
      return earlyVal
    if earlyVal == -1 and lateVal == -1: badExit(cryoKey)
      
    earlyDatTime = datetime.datetime(**earlyTime)
    lateDatTime = datetime.datetime(**lateTime)
    
    #compute the time difference in seconds directly because the timedelta object method "totalseconds"
    #was implemented in python 2.7. Mac OS 10.6 ships with python 2.6 and so this method doesn't exist on those
    #running Snow Leopard or older. 
    td = eventTime - earlyDatTime
    eventToEarly = (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
    td = lateDatTime - earlyDatTime
    totalDiff = (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
    
    return earlyVal + eventToEarly * (lateVal - earlyVal) / totalDiff
    
    
    
if __name__ == '__main__':
  theRet = main(*sys.argv[1:])
  if theRet != None:
    try:
      for r in theRet:
        print r
    except:
      print theRet
