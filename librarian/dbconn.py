#!/usr/bin/env python
"""Database connectivity for Librarian.

This module contains all the classes and miscellany necessary for
Librarian to connect to a shared backend RDBMS for metadata.  It
is not designed to hold raw content, just the file names, version
history, checksums, etc.

Schema is encoded in the classes listed below.
"""

import MySQLdb, datetime
import os
import sys
import datetime
import uuid
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
Base = declarative_base()

class Project(Base):
  __tablename__ = "projects"
  id = Column(Integer, primary_key = True)
  name = Column(String(250), nullable = False)
  owner = Column(String(250), nullable = False)
  created = Column(DateTime)
  updated = Column(DateTime)
  comments = Column(String(4097), nullable = True)

  def __str__(self):
    t = """name: %(name)s
owner: %(owner)s
created: %(created)s
updated: %(updated)s"""

    d = {"name": self.name,
         "owner": self.owner,
         "created": self.created,         
         "updated": self.updated,
         "comments": self.comments}

    return t % d

class Directory(Base):
  __tablename__ = "directory"
  id = Column(String(256), primary_key = True)
  uniqid = Column(String(256), nullable = False)
  dirname = Column(String(250), nullable = False)
  status = Column(String(250), nullable = False)
  created = Column(DateTime)
  updated = Column(DateTime)
  comments = Column(String(4097), nullable = True)
  project_id = Column(Integer, ForeignKey("projects.id"))
  project = relationship(Project)

  def __str__(self):
    return self.dirname + "\t" + self.status + "\t" + str(self.created) + "\t" + str(self.updated) + "\t" + self.uniqid

class Fileinfo(Base):
  __tablename__ = "fileinfo"
  id = Column(Integer, primary_key = True)
  filename = Column(String(250), nullable = False)
  hashcode = Column(String(250), nullable = False)
  size = Column(Integer, nullable = False)
  directory_id = Column(Integer, ForeignKey("directory.id"))
  directory = relationship(Directory)

  def __str__(self):
    return self.filename + "\t" + str(self.size) + "\t" + self.hashcode

#
# Library is a generic set of metadata operations
#
class Library:
  """Represents a live database conn with Librarian-specific operators."""

  #
  def __init__(self, username, password, host, port = 3306):
    self.user = username
    self.pswd = password
    self.host = host
    self.port = int(port)

    self.engine = create_engine("sqlite:///foo.db")
    Base.metadata.create_all(self.engine)
    Base.metadata.bind = self.engine
    DBSession = sessionmaker(bind=self.engine)
    self.session = DBSession()
    
    #try:
    #    self.db = MySQLdb.connect(host=self.host, port=self.port, user=self.user,
    #                                passwd=self.pswd, db='librarian')
    #except:
    #    raise Exception('Invalid credentials for librarian database')

  #
  # List all projects
  #
  def ls(self):
    ''' returns a generator listing all librarian projects '''
    for p in self.session.query(Project).all():
      yield p

  #
  # Get details about a specific project
  #
  def getProject(self, projectName):
    """Returns a specific Project and all its details"""
    return self.session.query(Project).filter(Project.name==projectName).one()

  #
  # Create a brand-new project
  #
  def createProject(self, projectname, owner, comments=''):
    ''' Creates a new project in the database. This function should be called
    after appropriate space has been allocated on the S3 bucket
    '''
    if projectname in map(lambda x: x.name, self.ls()):
      raise Exception('Project already exists!')

    new_project = Project(name=projectname, created=datetime.datetime.now(), updated=datetime.datetime.now(), owner=owner, comments=comments)
    self.session.add(new_project)
    self.session.commit()

  #
  # List all directories associated with a project
  #
  def lsDirs(self, projectName):
    p = self.getProject(projectName)
    distinctDirs = self.session.query(Directory.dirname).filter(Directory.project==p).distinct()
    for ddir in distinctDirs:
      maxDate = self.session.query(func.max(Directory.updated)).filter(Directory.project==p).filter(Directory.dirname==ddir.dirname)
      yield self.session.query(Directory).filter(Directory.dirname==ddir.dirname).filter(Directory.updated==maxDate).one()
    
  #
  # Get details about a specific directory
  #
  def getDirectory(self, projectName, dirName):
    maxDate = self.session.query(func.max(Directory.updated))
    ds = self.session.query(Directory).filter(Project.name==projectName).filter(Directory.dirname==dirName).filter(Directory.updated==maxDate).all()
    if len(ds) == 0:
      return None
    else:
      return ds[0]

  #
  # Get details about a specific directory
  #
  def getAllDirectoryVersions(self, projectName, dirName):
    return self.session.query(Directory).filter(Project.name==projectName).filter(Directory.dirname==dirName).all()

  #
  # Get details about a specific directory
  #
  def getDirectoryWithVersion(self, projectName, dirName, uniqid):
    return self.session.query(Directory).filter(Project.name==projectName).filter(Directory.dirname==dirName).filter(Directory.uniqid==uniqid).one()

  #
  # Create a new (or updated) directory, along with the accompanying files.
  #
  def createDirectory(self, projectName, dirName, status, comments, filelist, createDirUuid):
    p = self.getProject(projectName)
    old_dir = self.getDirectory(projectName, dirName)
    createdTime = datetime.datetime.now()
    if old_dir is not None:
      createdTime = old_dir.created

    new_dir = Directory(id=createDirUuid,
                        dirname=dirName,
                        uniqid=createDirUuid,
                        status=status,
                        created=createdTime,
                        updated=datetime.datetime.now(),
                        comments=comments,
                        project=p)

    new_files = map(lambda x: Fileinfo(filename=x[1],
                                       hashcode=x[2],
                                       size=x[3],
                                       directory=new_dir),
                    filelist)

    self.session.add(new_dir)
    map(lambda x: self.session.add(x), new_files)
    self.session.commit()

  #
  # List all files associated with a project/dir pair
  #
  def lsFiles(self, d):
    for f in self.session.query(Fileinfo).filter(Fileinfo.directory==d).all():
      yield f
    
  #
  # Get details about a specific file
  #
  def getFile(self, projectName, dirName, fname):
    return self.session.query(Fileinfo).filter(Project.name==projectName).filter(Directory.name==dirName).filter(Fileinfo.name==fname).one()





