#!/usr/bin/env python
"""AWS downloader code

This module contains all the code needed to fetch a file (reliably)
from AWS.

"""

import boto, sys, os
from boto.s3.key import Key
from boto.s3.connection import S3Connection
from boto.s3.resumable_download_handler import ResumableDownloadHandler
from boto.gs.resumable_upload_handler import ResumableUploadHandler
import hashlib

def hashfile(fname, blocksize=65536):
  hasher = hashlib.md5()
  f = open(fname)
  try:
    buf = f.read(blocksize)
    while len(buf) > 0:
      hasher.update(buf)
      buf = f.read(blocksize)
    return hasher.hexdigest()
  finally:
    f.close()

#
#
#
class FileCopyCallbackHandler(object):
  """Outputs progress info for large AWS copy requests."""
  def __init__(self, upload):
    if upload:
      self.announce_text = 'Uploading'
    else:
      self.announce_text = 'Downloading'

  def call(self, total_bytes_transferred, total_size):
    sys.stderr.write("Total bytes transferred: " + str(total_bytes_transferred) + " total size: " + str(total_size) + "\r")
    if total_bytes_transferred == total_size:
      sys.stderr.write('\n')

#
#
#
class AWS(object):
  """The Generic AWS handler object"""
  def __init__(self, access_key, secret_key):
    self.access_key = access_key
    self.secret_key = secret_key
    self.s3 = S3Connection(
      aws_access_key_id = self.access_key,
      aws_secret_access_key = self.secret_key)
    self.storageBucketName = "deepdive-librarian"

  #
  def uploadAWSFileIfNeeded(self, projname, dirname, dirUuid, localFilePath, localFileName, localFileHash):
    """Reliably uploads a single AWS file to a given AWS path, from a local file"""
    cb = FileCopyCallbackHandler(False).call

    fileHash = ""
    fileHash = hashfile(localFilePath)

    resumableDataFile = os.path.join(localFilePath + ".resumableInfo.")
    keyname = "storage" + "/" + projname + "/" + dirname + "/" + dirUuid + "/" + localFileName + "/" + fileHash
    deepDiveBucket = self.s3.get_bucket(self.storageBucketName)
    k = Key(deepDiveBucket)
    k.key = keyname

    resumableUploader = ResumableUploadHandler(tracker_file_name=resumableDataFile, num_retries=5)
    with open(localFilePath) as fp:
      k.set_contents_from_file(fp, headers={}, replace=False, cb=cb, num_cb=10)
    

  #
  def downloadAWSFile(self, filedesc, localDstPath):
    """Reliably downloads a single AWS file to a given filesystem path, from an AWS path"""
    isDone = False
    while not isDone:
      try:
        self.__downloadAWSFileAttempt(filedesc, localDstPath)
        isDone = True
      except Exception as exc:
        print "AWS Download Exception:", exc
      
  #
  #
  #
  def __downloadAWSFileAttempt(self, filedesc, localDstPath):
    """Nitty-gritty needed to grab the AWS file.  This might fail if the connection fails."""
    cb = FileCopyCallbackHandler(False).call
  
    resumableDataFile = os.path.join(localDstPath + ".resumableInfo." + filedesc.filename)
    keyname = "storage" + "/" + filedesc.directory.project.name + "/" + filedesc.directory.dirname + "/" + filedesc.directory.uniqid + "/" + filedesc.filename + "/" + filedesc.hashcode

    deepDiveBucket = self.s3.get_bucket(self.storageBucketName)  
    k = deepDiveBucket.get_key(keyname)

    resumableDownloader = ResumableDownloadHandler(tracker_file_name=resumableDataFile, num_retries=5)
    fp = open(localDstPath, "a")
    try:
      k.get_contents_to_file(fp, headers={}, cb=cb, num_cb=100, res_download_handler=resumableDownloader)
    finally:
      fp.close()


