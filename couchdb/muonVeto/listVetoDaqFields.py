#!/usr/bin/env python

from couchdbkit import Server, Database
import sys

s = Server('https://edwdbik.fzk.de:6984')
db = s['muonvetohardwaremap']
vr = db.view('map/keys', reduce = True, group=True)
for row in  vr:
  if row['key'] != '_id' and row['key'] != '_rev':
    print row['key']

