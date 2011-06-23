#!/usr/bin/env python

from couchdbkit import Server, Database
import sys, math, os, datetime
from ROOT import *  #use ROOT to plot data. Also save an output ROOT file containing all of the data for external use

def main(*argv):
  '''
    Creates ROOT Plots of the cryogenic variables that are returned by the database/cryo_2/getData view. 
    The data plotted are from the last four hours, displayed in local time.
    You should provide two arguments. 
    1. the directory location where to save the output .png files and ROOT file (ex: /path/to/folder/)
    2. the name of the ROOT file (ex: lastfourhours.root)
    
  '''
  gROOT.SetBatch(True)  #turn graphics OFF!
  
  s = Server('http://edwdbik.fzk.de:5984')
  db = s['automat']
  
  #set output ROOT file and output path for the images
  fout = TFile(os.path.join(argv[0], argv[1]), 'recreate')  
  dout = argv[0]  #the output directory

  #get list of cryo variables available from the 'getData' view
  #and create a ROOT::TGraph object to store the results 
  #and then group them in a dictionary for easy retrieval.
  vr = db.view('cryo_2/getData', group_level=1)

  graphdict = dict()
  for row in vr:
    g = TGraph()
    g.SetName(row['key'][0])
    graphdict[row['key'][0]] = {'graph':g, 'count':0}
  
  #get the current time and the time 4 hours ago
  ct = datetime.datetime.utcnow()  #current time
  dt = datetime.timedelta(hours=4) #delta time
  pt = ct - dt #past time

  #rootTimeOffset... so that root displays the date properly
  rt = datetime.datetime(1995, 1, 1)
  ut = datetime.datetime(1970, 1, 1)
  dt = ut - rt
  toffset = (dt.microseconds + (dt.seconds + dt.days * 24 * 3600) * 10**6) / 10**6


  #now get the data from the last 4 hours, using view options to 
  #set the range of return. (You must know, a priori, what the 'getData' view actually
  #returns in order to program this -- this is
  #also the case for when i used the view above. The output for each view is different since it
  #is programmed by somebody.)
  
  c = TCanvas('c1')
  
  for k in graphdict.iterkeys():
    skey = [k, pt.year, pt.month, pt.day, pt.hour, pt.minute, 0]
    ekey = [k, ct.year, ct.month, ct.day, ct.hour, ct.minute+1, 0]
    
    vr = db.view('cryo_2/getData', reduce=False, startkey=skey, endkey=ekey)
  
    g = graphdict[k]['graph']
    count = graphdict[k]['count']
    
    for row in vr:
      g.SetPoint(count, row['key'][6] - toffset, row['value'])
      count = count + 1

    graphdict[k]['count'] = count
    g.GetXaxis().SetTimeDisplay(True)
    g.Draw('ap')
    c.SaveAs( os.path.join(dout, k + '.png'), 'png')
    fout.cd()
    g.Write()
  
  
  fout.Close()


if __name__ == '__main__':
  main(*sys.argv[1:])