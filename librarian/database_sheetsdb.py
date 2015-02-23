######################################################################################
#                                                                                    #
# A temprorary implementation which uses google sheets as the database for librarian #
#                                                                                    #
#                                                                                    #
# Written by - Abhinav Rastogi, 02/16/2015                                           #
#                                                                                    #
######################################################################################


import os
from urllib2 import urlopen
from subprocess import call
import json
import re

read_key = os.getenv('SHEETSDB_KEY_READ')

LIBRARIAN_SCHEMA = {
'Engagements':
    ['project', 'date_started', 'owner', 'comments'], 

'IncomingData':
    ['project', 'dataset', 'version', 'timestamp', 'urls', 'checksums', 'metadata_url', 'comments', 'user', 'hostname'],
'OutgoingData':
    ['project', 'dataset', 'version', 'timestamp', 'urls', 'checksums', 'metadata_url', 'comments', 'user', 'hostname']
}

# Insert into sheet
def insert(table, **kwargs):
    row = dict(kwargs)
    if table not in LIBRARIAN_SCHEMA:
        raise Exception("Table not found.")
    if not set(row.keys()) <= set(LIBRARIAN_SCHEMA[table]):
        raise Exception("Schema doesn't match. Insert aborted.")
    cmd = ['sheetsdb', 'insert', table]
    for k, v in row.iteritems():
        cmd.append('%s=%s' % (k, str(v) if v is not None else ''))
    call(cmd)


# Query from sheet based on an attribute
def query(table, **kwargs):
    row = dict(kwargs)
    params = []
    for k, v in row.iteritems():
        params.append(k + '%3D' + repr(v))
    query = 'select%20*'
    if len(params) > 0:
        query += '%20where%20' + '%20and%20'.join(params)
    url = 'https://docs.google.com/spreadsheets/d/' + read_key + \
        '/gviz/tq?tq=' + query + '&sheet=' + table
    resp = urlopen(url)
    print url
    res = resp.read()[39:-2]
    # Parse the javascript dates
    hasDate = re.search(r'new Date\([0-9,]*\)', res)
    while hasDate:
        a,b = hasDate.span()
        y, m, d = map(int, res[a+9:b-1].split(','))
        res = res[:a]+'"'+str(m+1)+'-'+str(d)+'-'+str(y)+'"'+res[b:]
        hasDate = re.search(r'new Date\([0-9,]*\)', res)
    # load the json object
    res = json.loads(res)
    cols = map(lambda x:x[u'label'], res[u'table'][u'cols'])
    rows = [map(lambda x:x[u'v'] if x else None, r[u'c']) for r in res[u'table'][u'rows']]
    return cols, rows
    
if __name__=='__main__':
    # insert('Engagement', project='memex', date_started='2014-09-01', owner='mjc', comments='This will be big!')
    # insert('IncomingData', project='memex', dataset='small sample of backpage', version=None, timestamp='20140901_123456.789012', checksums='MD5...', urls='s3:dd-incoming/memex/small_sample_of_backpage/v_0000/data.tsv', comments='more data expected later')
    # insert('OutgoingData', project='memex', dataset='Memex ht basic attrs', timestamp='20141130_123456.789012', checksums='MD5:...', urls='s3:dd-outgoing/memex/memex_ht_basic_attrs/v_0000/data_0000.tsv', metadata_url='s3:dd-outgoing/memex/memex_ht_basic_attrs/v_0000/report.pdf', comments='First shipment!  This reflects input backpage data from the large-backpage-crawl up through Nov-1-2014')
    print query('ActivityLog', A=0)
