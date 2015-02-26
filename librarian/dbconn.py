#!/bin/python
"""Database connectivity for Librarian.

This module contains all the classes and miscellany necessary for
Librarian to connect to a shared backend RDBMS for metadata.  It
is not designed to hold raw content, just the file names, version
history, checksums, etc.

"""


import  boto, json, os.path


defaultAWSRegion = "us-west-2"


class DBConn:
  """Represents a live database conn with Librarian-specific operators."""

  def __init__(self, connDetails):
    self.connDetails = connDetails
    self.conn = 10

  def listProjects(credential):
    """List all the Librarian project names"""
    conn = boto.rds.connect_to_region(
      defaultAWSRegion,
      aws_access_key_id=credential.awsKeyId,
      aws_secret_access_key=credential.awsSecretKey)

    try:
      pass
    finally:
      conn.close()
