#!/usr/bin/env python
"""Librarian Client Version 0.01

Librarian takes care of all files that leave/enter engagements.  When
a partner provides a new datafile (as with Memex ads), they get added
to Librarian.  When we ship extracted data elsewhere, they get added
to Librarian.

It can also be used to track standard utility files, like Wikipedia or
Freebase dumps.

It should NOT be used to hold temporary or working files.
"""

import argparse, boto, json, os.path, MySQLdb

##
# GLOBALS
##
configFilename = os.path.abspath(os.path.expanduser("~/.librarian"))
configDict = {"credentials":[]}

###############################################
class ConfigError(Exception):
  """ConfigError is a basic Exception wrapper class for this application"""
  def __init__(self, msg):
    self.msg = msg


class AWSInfo:
  """AWSInfo is a simple container class for a named AWS key pair"""
  def __init__(self, credentialsName, awsKeyId, awsSecretKey):
    self.credentialsName = credentialsName
    self.awsKeyId = awsKeyId
    self.awsSecretKey = awsSecretKey

##################################################

def loadConfig():
  """Grab config info from the ondisk file."""
  if not os.path.exists(configFilename):
    raise ConfigError("Librarian config file does not exist.  Invoke librarian --init to create")
    
  configFile = open(configFilename)
  try:
    global configDict
    configDict = json.loads(configFile.read())
  finally:
    configFile.close()


def saveConfig():
  """Save config info to disk file."""
  configFile = open(configFilename, "w")
  try:
    configFile.write(json.dumps(configDict))
  finally:
    configFile.close()


def configInit():
  """Create the local .librarian config file, if none previously existed"""
  if os.path.exists(configFilename):
    raise ConfigError("Cannot init.  Librarian config file already exists at", configFilename)
  saveConfig()


def addCredentials(credentialName, awsKeyId, awsSecretKey):
  """Add a new credential triple to the config file for later use"""
  loadConfig()
  global configDict
  configDict["credentials"].append((credentialName, awsKeyId, awsSecretKey))
  saveConfig()


def checkS3():
  """Ensure we have valid S3 access"""
  loadConfig()


def checkMetadata():
  """Ensure we have valid access to the Librarian metadata."""
  loadConfig()


def put(fname, project, comment):
  """Check a file into Librarian"""
  checkMetadata()
  print "Put a file called", fname, "into project", project, "with comment", comment


def get(fname, project):
  """Get a file from Librarian"""
  checkMetadata()  
  print "Get a file called", fname, "from project", project


def projectLs():
  """List all Librarian files for a single project"""
  checkMetadata()  
  print "List all projects"


def ls(projectname):
  """List all Librarian projects"""
  checkMetadata()  
  print "List all files in a project called", projectname


#
# main()
#
if __name__ == "__main__":
  usage = "usage: %prog [options]"

  # Setup cmdline parsing
  parser = argparse.ArgumentParser(description="Librarian stores data")
  parser.add_argument("--put", nargs=3, metavar=("filename", "project", "comment"), help="Puts a <filename> into a <project> with a <comment>")
  parser.add_argument("--get", nargs=2, metavar=("filename", "project"), help="Gets a <filename> from a <project>")
  parser.add_argument("--config", nargs=1, metavar=("configfile"), help="Location of the Librarian config file")
  parser.add_argument("--lscreds", action="store_true", help="List all known credentials")
  parser.add_argument("--addcred", nargs=3, metavar=("credential-name", "aws_access_key_id", "aws_secret_access_key"), help="Stores an AWS pair under name <credential-name>")
  parser.add_argument("--ls", nargs=1, metavar=("project"), help="List all the files in a <project>")
  parser.add_argument("--pls", action="store_true", default=False, help="List all projects")
  parser.add_argument("--init", action="store_true", default=False, help="Create the initial config file")  
  parser.add_argument("--version", action="version", version="%(prog)s 0.1")

  # Invoke either get() or put()
  args = parser.parse_args()
  try:
    if args.config is not None:
      configFilename = os.path.abspath(args.config)
      
    if args.init:
      configInit()
    elif args.addcred is not None and len(args.addcred) == 3:
      addCredentials(args.addcred[0], args.addcred[1], args.addcred[2])
    elif args.pls:
      projectLs()
    elif args.ls is not None:
      ls(args.ls)
    elif args.put is not None and len(args.put) > 0:
      put(args.put[0], args.put[1], args.put[2])
    elif args.get is not None and len(args.get) > 0:
      get(args.get[0], args.get[1])
    elif args.lscreds:
      loadConfig()
      print "There are", len(configDict["credentials"]), "credential(s) available"
      for idx, awsCred in enumerate(configDict["credentials"]):
        print " ", idx, awsCred[0]
    else:
      parser.print_help()
  except ConfigError as e:
    print e.msg
    
    

    

  

  


  
