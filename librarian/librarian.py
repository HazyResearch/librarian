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

import argparse, boto, json, os.path, MySQLdb, dbconn, hashlib, random, time, sys, shutil
from file import Fileinfo
from aws import AWS
import dialog
import uuid
import pickle
from aws import hashfile
from dialog import q

##
# GLOBALS
##
configDir = os.path.abspath(os.path.expanduser("~/.librariandir"))
tmpDir = os.path.abspath(os.path.join(configDir, "tmpdir"))
configFilename = os.path.abspath(os.path.join(configDir, ".librarian"))
configDict = {}

###############################################
class ConfigError(Exception):
  """ConfigError is a basic Exception wrapper class for this application"""
  def __init__(self, msg):
    self.msg = msg

#
#
#
def __formulateLibrarianFilename(fileId):
  return "opaque_file." + str(fileId)

#
#
#
def loadConfig():
  """Grab config info from the ondisk file."""
  if not os.path.exists(configFilename):
    raise ConfigError("Librarian config file does not exist.  Invoke librarian --init to create")

  if not os.path.exists(configDir):
    raise ConfigError("Librarian config directory does not exist.  Invoke librarian --init to create")
    
  configFile = open(configFilename)
  try:
    global configDict
    configDict = json.loads(configFile.read())
  finally:
    configFile.close()

  global awsConn
  awsConn = AWS(configDict["awscredentials"][0], configDict["awscredentials"][1])      

  __handleInterruptedPut()


#
#
#
def saveConfig():
  """Save config info to disk file."""
  configFile = open(configFilename, "w")
  try:
    configFile.write(json.dumps(configDict))
  finally:
    configFile.close()


#
#
#
def configInit(awsKeyId, awsSecretKey, dbUser, dbPasswd, dbHost, dbPort):
  """Create the local .librarian config file, if none previously existed"""
  if os.path.exists(configFilename):
    raise ConfigError("Cannot init.  Librarian config file already exists at " + configFilename)
  if os.path.exists(configDir):
    raise ConfigError("Cannot init.  Librarian config directory already exists at " + configDir)
  os.mkdir(configDir)
  os.mkdir(tmpDir)
  
  global configDict
  configDict["awscredentials"] = (awsKeyId, awsSecretKey)
  configDict["dbcredentials"] = {"user":dbUser, "password":dbPasswd, "host":dbHost, "port":dbPort}
  saveConfig()

#
#
#
def checkMetadata():
  """Ensure we have valid access to the Librarian metadata."""
  loadConfig()
  global library
  c = configDict["dbcredentials"]
  library = dbconn.Library(c["user"], c["password"], c["host"], c["port"])

#####################################################################
#####################################################################
#####################################################################

#
# Invoked when we detect a put() that was not completed.
#
def __handleInterruptedPut():
  #
  # An interrupted put() can be in one of several states:
  # 1) The put() started, but there is no file information available.
  #    In this case, we should abort the interrupted put().
  # 2) The put() started, and there is file information available,
  #    but the transfer did not complete.  In this case, we
  #    should complete the interrupted transfer and then complete
  #    the rest of the put().
  # 3) The put() started, and the file transfer completed, but
  #    the metadata was not inserted.  In this case, we should
  #    insert the metadata and complete the rest of the put().
  #
  #    (Metadata insert should be idempotent.  I.e., multiple
  #     inserts of identical data changes nothing.)
  for tipDir in os.listdir(tmpDir):
    fullTipDir = os.path.abspath(tipDir)
    deetsFile = os.path.join(fullTipDir, "deets")
    transferDoneFile = os.path.join(fullTipDir, "transferDone")

    # Are we in Case 1?
    inCase1 = True
    try:
      if os.path.exists(deetsFile):
        with open(deetsFile) as fp:
          filedesc = pickle.load(fp)
          localFname = pickle.load(fp)
          inCase1 = False
    except Exception as exc:
      pass

    # Are we in Case 2?
    inCase2 = not os.path.exists(transferDoneFile) and not inCase1

    # Are we in Case 3?
    inCase3 = os.path.exists(transferDoneFile) and not inCase1

    # Handle each case
    if inCase1:
      shutil.rmtree(tipDir)
    elif inCase2:
      awsConn.uploadAWSFile(filedesc, localFname)
      with open(os.path.join(tipDir, "transferDone"), "w") as fp:
        pass
      library.put(filedesc, localFname)
      shutil.rmtree(tipDir)      
    elif inCase3:
      library.put(filedesc, localFname)
      shutil.rmtree(tipDir)      

#
# There are 6 steps to a recoverable file transfer
#
def __processPut(filedesc, localFname):
  """Partially-recoverable data transfer to Librarian server"""
  # Step 1.  Create a 'transfer-in-progress' directory.  
  tipDir = os.path.join(configDir, "tmp." + random.randint(0, 99999999))
  os.mkdir(tipDir)

  # Step 2.  Write to disk the details of the file we're about to transfer
  with open(os.path.join(tipDir, "deets"), "w") as fp:
    pickle.dump(fp, filedesc)
    pickle.dump(fp, localFname)

  # Step 3.  Transfer the file
  awsConn.uploadAWSFile(filedesc, localFname)
  
  # Step 4.  Write to disk the fact we're done transferring
  with open(os.path.join(tipDir, "transferDone"), "w") as fp:
    pass

  # Step 5.  Commit the new file info to the library
  library.put(filedesc, localFname)
  
  # Step 6.  Delete the 'transfer-in-progress' directory.
  shutil.rmtree(tipDir)
  

#####################################################################
#####################################################################
#####################################################################

#
# List all Librarian projects
#
def ls():
  """List all Librarian projects"""
  checkMetadata()
  for proj in library.ls():
    print "\t".join([proj.name,
                     proj.owner,
                     "created " + str(proj.created),
                     "updated " + str(proj.updated)])
  print

#
# Examine a Librarian object
#
def examine(libid, comments=False):
  checkMetadata()
  # Is it a project, a directory, or a versioned directory?
  parts = map(lambda x: x.strip(), libid.split(":"))
  
  if len(parts) == 1:
    # It's a project
    p = library.getProject(parts[0])
    print p
    if comments:
      print "comments: " + p.comments
      
    if p is None:
      print "Could not find any Librarian project with name '" + libid + "'"
    else:
      allDirs = library.lsDirs(p.name)
      ingestedDirs = filter(lambda x: x.status == "ingest", allDirs)
      outgestedDirs = filter(lambda x: x.status == "outgest", allDirs)

      print "There are", len(ingestedDirs), "ingested directories"
      for d in ingestedDirs:
        print d
        if comments:
          print "comments: " + d.comments
        print
      print
      print "There are", len(outgestedDirs), "outgested directories"
      for d in outgestedDirs:
        print d
        if comments:
          print "comments: " + d.comments
        print

  elif len(parts) == 2:
    # It's a directory
    p = library.getProject(parts[0])
    print p
    if comments:
      print "comments: " + p.comments
    if p is None:
      print "Could not find any Librarian project with name '" + parts[0] + "'"
    else:
      d = library.getDirectory(p.name, parts[1])
      if d is None:
        print "Could not find any Librarian directory with name '" + parts[1] + "'"
      else:
        print d
        if comments:
          print "comments: " + d.comments
        print
        files = library.lsFiles(d)
        for f in files:
          print "\t" + f.filename + "\t" + str(f.size) + "\t" + f.hashcode

  elif len(parts) == 3:
    # It's a versioned directory
    p = library.getProject(parts[0])
    print p
    if comments:
      print "comments: " + p.comments
    if p is None:
      print "Could not find any Librarian project with name '" + parts[0] + "'"
    else:
      if parts[2] == "all":
        for d in library.getAllDirectoryVersions(p.name, parts[1]):
          print d
          if comments:
            print "comments: " + d.comments
          for f in library.lsFiles(d):
            print "\t" + f.filename + "\t" + str(f.size) + "\t" + f.hashcode
          print
      else:
        d = library.getDirectoryWithVersion(p.name, parts[1], parts[2])
        if d is None:
          print "Could not find any Librarian directory with name '" + parts[1] + "'"
        else:
          print d
          if comments:
            print "comments: " + d.comments
          files = library.lsFiles(d)
          for f in files:
            print "\t" + f.filename + "\t" + str(f.size) + "\t" + f.hashcode
  else:
    print "Cannot determine what kind of Librarian object you want to examine"

#
#
#
def getFileByName(fname, project, dstPath):
  """Get file data from Librarian.  Search by name and project."""
  checkMetadata()  
  filedesc = library.getFileInfo(project, fname)
  if os.path.isdir(dstPath):
    dstFilename = os.path.join(dstPath, filedesc.filename)
  else:
    dstFilename = dstPath

  print "Found file..."
  print filedesc
  print
  print "Copying file to", dstFilename
  awsConn.downloadAWSFile(filedesc, dstFilename)

#
#
#
def getFileByID(fileId, dstPath):
  """Get file data from Librarian.  Search by Librarian ID."""
  checkMetadata()
  filedesc = library.getFileInfo(fileId)
  if os.path.isdir(dstPath):
    dstFilename = os.path.join(dstPath, filedesc.filename)
  else:
    dstFilename = dstPath
  
  print "Found file..."
  print filedesc
  print
  print "Copying file to", dstFilename
  awsdownloader.downloadAWSFile(filedesc, dstFilename)

#
#
#
def projectLs(projectName):
  """List all Librarian files for a single project"""
  checkMetadata()
  print "Project", projectName
  for filedesc in library.getFilesInProject(projectName):
    print "  ", filedesc.filename
    print "  ", filedesc.size, "bytes"
    print "  ", "added on", filedesc.date
    for k, v in filedesc.iteritems():
      print "  ", k, "=", v
    print
    print


#
#
#
def createProject(name, owner):
  """Create a brand-new project"""
  checkMetadata()
  comment = q("Please describe the project", qtype="desc")
  library.createProject(name, owner, comment)
  print "Created project", name

#
# The 'recoverable transfer' step
#
def executeTransfer(projname, dirname, inVsOutGest, comment, fnameData):
  # Step 1.  Create a 'transfer-in-progress' directory.  
  tipDir = os.path.join(configDir, "tmp." + str(random.randint(0, 99999999)))
  os.mkdir(tipDir)

  # Step 2.  Write to disk the details of the file we're about to transfer
  todoDetails = {"projname": projname,
                 "dirname": dirname,
                 "uuid": uuid.uuid4().hex,
                 "inVsOutGest": inVsOutGest,
                 "comment": comment,
                 "fnameData": fnameData}
  with open(os.path.join(tipDir, "deets"), "w") as fp:
    pickle.dump(todoDetails, fp)

  recoverTransfer(tipDir)

#
# Execute (or recover) a (potentially-interrupted) transfer
#
def recoverTransfer(tipDir):
  # Load in the transfer info
  deetFile = os.path.join(tipDir, "deets")
  todoDetails = {}
  with open(deetFile) as fp:
    todoDetails = pickle.load(fp)

  projname = todoDetails["projname"]
  dirname = todoDetails["dirname"]
  inVsOutGest = todoDetails["inVsOutGest"]
  comment = todoDetails["comment"]
  uuid = todoDetails["uuid"]
  fnameData = todoDetails["fnameData"]

  # Transfer the files
  for fnameDatum in fnameData:
    awsConn.uploadAWSFileIfNeeded(projname, dirname, uuid, fnameDatum[0], fnameDatum[1], fnameDatum[2])

  # Commit info to the database
  library.createDirectory(projname, dirname, inVsOutGest, comment, fnameData, uuid)

  # Done
  shutil.rmtree(tipDir)

#
# copy data out of Librarian
#
def cp(librariandir, localdir):
  if os.path.exists(localdir):
    raise Exception("Cannot copy to directory " + localdir + "; it already exists.")
  os.mkdir(localdir)
  
  checkMetadata()
  p = None
  d = None
  parts = map(lambda x: x.strip(), librariandir.split(":"))
  if len(parts) == 1:
    raise Exception("Must provide a Librarian directory, in the form Project:Dir(:version)")
  elif len(parts) == 2:
    p = library.getProject(parts[0])
    if p:
      d = library.getDirectory(p.name, parts[1])
  elif len(parts) == 3:
    p = library.getProject(parts[0])
    if p:
      d = library.getDirectory(p.name, parts[1], parts[2])

  print "Copying data from following Librarian directory:"
  print d
  for f in library.lsFiles(d):
    print "Copying", f.filename, "from Librarian to", localdir
    awsConn.downloadAWSFile(f, os.path.join(localdir, f.filename))
    print
  
  
#
# Take in a directory of files
#
def checkinDirectory(projname, dirname, localDir, inVsOutGest):
  checkMetadata()

  #
  # Prep the directory for checkin
  #
  absPath = os.path.abspath(localDir)
  fnameData = []
  for fname in filter(lambda x: not x.startswith(".") and os.path.isfile(os.path.join(absPath, x)), os.listdir(absPath)):
    try:
      fnameData.append((os.path.join(absPath, fname),
                        fname,
                        hashfile(os.path.join(absPath, fname)),
                        os.lstat(os.path.join(absPath, fname)).st_size))
    except Exception as exc:
      print exc
      pass
  
  #
  # Check to make sure the directory doesn't conflict with
  # one that's already there
  #
  curDir = library.getDirectory(projname, dirname)
  if curDir:
    if curDir.status != inVsOutGest:
      raise Exception("Cannot change the ingest/outgest status of a directory that already exists.")

  if inVsOutGest:
    print "Ingesting data for project " + projname + " under directory " + dirname
  else:
    print "Outgesting data for project " + projname + " under directory " + dirname    
  print "Processing", len(fnameData), "files from", localDir

  #
  # Grab comments from the user
  #
  obtainTypes = ["Data was obtained directly from data partner.",
                 "Data is result of SQL query against data partner database.",
                 "Data is result of running processing program over a raw partner file.",
                 "Data comes from some other source"]

  commentLines = []
  if inVsOutGest == "ingest":
    howObtained = q("How was this data obtained?", qtype="multi", args=obtainTypes)
    commentLines.append(obtainTypes[howObtained])

    if howObtained == 1:
      commentLines.append(q("Describe how data was obtained from partner (e.g., URL or scp path)", qtype="desc"))
    elif howObtained == 2:
      didRun = q("Did you run getPartnerTuples.py in order to run the query?", qtype="yn")
      if didRun:
        commentLines.append("User ran getPartnerTuples.py")
        commentLines.append("Output from getPartnerTuples.py: " + q("Please paste getPartnerTuples.py output here", qtype="desc"))
      else:
        commentLines.append("User did not run getPartnerTuples.py")
        commentLines.append("Ran query against the following database: " +
                            q("What database hostname did you run against?", qtype="desc") + ", with query: " +
                            q("What SQL query did you run?", qtype="desc"))
    elif howObtained == 3:
      didProcessRaw = q("Did you process a raw file tracked by Librarian?", qtype="yn")
      if didProcessRaw:
        commentLines.append("Processed raw file(s) from Librarian.")
        commentLines.append(q("What is the Librarian project, directory, and directory uniquid?", qtype="desc"))
      else:
        print
        print "It is extremely important to track all raw data inputs."
        print "Consider aborting and then adding the raw file."
        print
        shouldQuit = q("Do you want to quit, so that the raw file can be added?", qtype="yn")
        if shouldQuit:
          raise Exception("Raw data input was not tracked")
        else:
          print
          shouldContinue = q("Are you sure you want to continue without adding the raw file?", qtype="yn")
          if not shouldContinue:
            raise Exception("Raw data input was not tracked")
          else:
            commentLines.append(q("<sigh>  OK.  Describe the raw file you processed.", qtype="desc"))
          
      print
      print "It is important to track all data-processing code."
      print "Strongly consider adding your code to GitHub before continuing."
      print
      isInGit = q("Is the processing program checked into GitHub?", qtype="yn")
      if isInGit:
        commentLines.append("Processing program was checked into github")
        commentLines.append(q("What is the the Git repo and commit id for your processor", qtype="desc"))
      else:
        commentLines.append(q("<sigh>  OK.  Please describe your processing program.  Paste code if necessary.", qtype="desc"))
    elif howObtained == 4:
      commentLines.append(q("OK, please describe in detail how you obtained the structured file.", qtype="desc"))

  executeTransfer(projname, dirname, inVsOutGest, "\n".join(commentLines), fnameData)

  
#
# main()
#
if __name__ == "__main__":
  usage = "usage: %prog [options]"

  # Setup cmdline parsing
  parser = argparse.ArgumentParser(description="Librarian stores data")
  parser.add_argument("--init", nargs=6, metavar=("aws_access_key_id", "aws_secret_access_key", "dbuser", "dbpassword", "dbhost", "dbport"), help="Inititalized and stores an AWS keypair")
  parser.add_argument("--lscreds", action="store_true", help="List all known credentials")
  parser.add_argument("--ls", action="store_true", default=False, help="List all projects")
  parser.add_argument("--examine", nargs=1, metavar=("librarianobj"), help="Examine a given Librarian object")  
  parser.add_argument("--comments", action="store_true", default=False, help="Print comments?")  
  parser.add_argument("--cp", nargs=2, metavar=("librariandir", "localdir"), help="Copy data from a Librarian directory to a local dir")    
  parser.add_argument("--createproj", nargs=2, metavar=("name", "owner"), help="Create a new project")
  parser.add_argument("--ingest", nargs=3, metavar=("proj", "name", "localdir"), help="Create new ingest directory in a Librarian project")
  parser.add_argument("--outgest", nargs=3, metavar=("proj", "name", "localdir"), help="Create new outgest directory in a Librarian project")  
  parser.add_argument("--version", action="version", version="%(prog)s 0.1")

  # Invoke either get() or put()
  args = parser.parse_args()
  try:
    if args.init is not None and len(args.init) == 6:
      configInit(args.init[0],
                 args.init[1],
                 args.init[2],
                 args.init[3],
                 args.init[4],
                 args.init[5])
    elif args.lscreds:
      loadConfig()
      print "AWS CREDENTIALS"
      print "aws access key:", configDict["awscredentials"][0]
      print "aws secret access key:", configDict["awscredentials"][1]
    elif args.ls:
      ls()
    elif args.examine is not None and len(args.examine) > 0:
      examine(args.examine[0], comments=args.comments)
    elif args.cp is not None and len(args.cp[0]) > 0 and len(args.cp[1]) > 0:
      cp(args.cp[0], args.cp[1])
    elif args.createproj is not None and len(args.createproj) > 1:
      createProject(args.createproj[0], args.createproj[1])
    elif args.ingest is not None and len(args.ingest) == 3:
      checkinDirectory(args.ingest[0], args.ingest[1], args.ingest[2], "ingest")
    elif args.outgest is not None and len(args.outgest) == 3:
      checkinDirectory(args.outgest[0], args.outgest[1], args.outgest[2], "outgest")
    else:
      parser.print_help()
  except ConfigError as e:
    print e.msg
  except Exception as ex:
    print ex
    raise ex
    
