#!/usr/bin/env python

from couchdbkit import Server, Database
import sys

s = Server('https://edwdbik.fzk.de:6984')
db = s['edwdb']
vr = db.view('muonveto/daqmap', include_docs = True, reduce = False, limit = 1)
doc = vr.first()['doc']
for k,val in doc.items():
  if k != '_id' and k!= '_rev':
    print k

