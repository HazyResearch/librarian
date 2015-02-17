import os
from urllib2 import urlopen
from subprocess import call
import json

read_key = os.getenv('SHEETSDB_KEY_READ')

# Insert into sheet
def insert(table, **kwargs):
    row = dict(kwargs)
    cmd = ['./sheetsdb', 'insert', table]
    for k, v in row.iteritems():
        cmd.append(k + '=' + str(v))
    call(cmd)


# Query from sheet based on an attribute
def query(table, numcols, **kwargs):
    row = dict(kwargs)
    params = []
    for k, v in row.iteritems():
        params.append(k + '%3D' + repr(v))
    query = 'select%20' + '%2C'.join(map(chr, range(ord('A'),ord('A')+numcols))) 
    query += '%20where%20' + '%20and%20'.join(params)
    url = 'https://docs.google.com/spreadsheets/d/' + read_key + \
        '/gviz/tq?tq=' + query + '&sheet=' + table
    resp = urlopen(url)
    res = json.loads(resp.read()[39:-2])
    cols = map(lambda x:x[u'label'], res[u'table'][u'cols'])
    rows = [map(lambda x:x[u'v'], r[u'c']) for r in res[u'table'][u'rows']]
    return cols, rows
    

def add_Engagement():
    pass

def add_Incoming():
    pass
    
def add_Outgoing():
    pass
    
def add_ActivityLog():
    pass

print query('test', 2, A=11)
