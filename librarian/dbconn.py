#!/bin/python
"""Database connectivity for Librarian.

This module contains all the classes and miscellany necessary for
Librarian to connect to a shared backend RDBMS for metadata.  It
is not designed to hold raw content, just the file names, version
history, checksums, etc.

Schema:
'Engagements': ['id', 'name', 'date_started', 'owner', 'comments'], 

'IncomingData': ['id', 'project', 'name', 'version', 'timestamp', 
      'urls', 'checksums', 'metadata_url', 'comments', 'user', 'hostname']

'OutgoingData': ['id', 'project', 'name', 'version', 'timestamp', 
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
    try:
      for _ in xrange(c.execute( '''select name from Engagements''')):
        yield c.fetchone()[0]
    except:
      raise Exception('Database not available')
    c.close()
    
  def projectLs(self, project):
    ''' returns a generator listing all datasets and their versions in
        a librarian project. The generator yield a (name, version) tuple.
    '''
    c = self.db.cursor()

    def datasetQueryFor(table):
        return '''
        select ds.name, ds.version
          from %s ds
          join Engagements on ds.project = Engagements.id
         where Engagements.name = %%s
        ''' % (table)
    try:
      for _ in xrange(c.execute(datasetQueryFor('IncomingData') +
                    ' union ' + datasetQueryFor('OutgoingData'),
                    (project, project))):
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
    c.execute('''insert into Engagements values (%s, %s, %s, %s)''',
            (project, date, owner, comments))
    c.close()
    
