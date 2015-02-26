#!/bin/python
"""Database connectivity for Librarian.

This module contains all the classes and miscellany necessary for
Librarian to connect to a shared backend RDBMS for metadata.  It
is not designed to hold raw content, just the file names, version
history, checksums, etc.

Schema:
'Engagements': ['project', 'date_started', 'owner', 'comments'], 

'IncomingData': ['project', 'dataset', 'version', 'timestamp', 
      'urls', 'checksums', 'metadata_url', 'comments', 'user', 'hostname']

'OutgoingData': ['project', 'dataset', 'version', 'timestamp', 
      'urls', 'checksums', 'metadata_url', 'comments', 'user', 'hostname']

"""

import MySQLdb, datetime

HOST = "librarian-test-abhirast.cfovowditnjo.us-east-1.rds.amazonaws.com"

class DBConn:
  """Represents a live database conn with Librarian-specific operators."""

  def __init__(self, username, password, port = 3306):
    self.user = username
    self.pswd = password
    self.port = port
    try:
        self.db = MySQLdb.connect(host=HOST, port=self.port, user=self.user,
                                    passwd=self.pswd, db='librarian')
    except:
        raise Exception('Invalid credentials for librarian database')
  
  def ls(self):
    ''' returns a generator listing all librarian projects '''
    c = self.db.cursor()
    query = 'select project from Engagements'
    try:
      for _ in xrange(c.execute(query)):
        yield c.fetchone()[0]
    except:
      raise Exception('Database not available')
    c.close()
    
  def projectLs(self, project):
    ''' returns a generator listing all datasets and their versions in
        a librarian project. The generator yield a (dataset, version) tuple.
    '''
    c = self.db.cursor()
    
    inQuery = 'select dataset, version from IncomingData where project=' \
        + repr(project)
    outQuery = 'select dataset,version from OutgoingData where project=' \
        + repr(project)
    query = inQuery + ' UNION ' + outQuery
    
    try:
      for _ in xrange(c.execute(query)):
        yield c.fetchone()[0]
    except:
      raise Exception('Database not available')
    c.close()
    
  def createProject(self, project, comments=''):
    ''' Creates a new project in the database. This function should be called
        after appropriate space has been allocated on the S3 bucket
    '''
    if project in self.ls():
      raise Exception('Project already exists!')
    c = self.db.cursor()
    date = datetime.date.today()
    owner = self.user
    command = '''insert into Engagements values (%s, %s, %s, %s)'''
    c.execute(command, (project, date, owner, comments))
    c.close()
    
