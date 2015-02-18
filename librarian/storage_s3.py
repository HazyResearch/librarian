#!/usr/bin/env python
# upload-s3.py -- Librarian script that takes care of uploading data to AWS S3

import boto
import boto.s3.connection
import os

def upload(local_path, project, name):
    # get the keys
    access_key = os.getenv('AWS_KEY')
    secret_key = os.getenv('AWS_SECRET_KEY')

    conn = boto.s3.connection.S3Connection(
        aws_access_key_id = access_key,
        aws_secret_access_key = secret_key,
        calling_format = boto.s3.connection.OrdinaryCallingFormat(),
        )
    
    # each project has its own bucket
    bucket = conn.lookup(project)
    if bucket is None:
        print 'Error bucket was owned\n\n'
        bucket = conn.create_bucket(project)
        key = bucket.new_key(name)
    else:
        key = bucket.get_key(name)
        i = 0
        while key is not None:
            i += 1
            key = bucket.get_key(name+'_'+str(i))
        key = bucket.new_key(name+'_'+str(i))
    # check if a file with the same name exists. If yes, generate a new name
    # Can replace this scheme by appending a random string to the end if a large
    # number of files is expected
    
        
    key.set_contents_from_filename(local_path)
    key.set_acl('public-read')
    url = key.generate_url(expires_in=0, query_auth=False)
    return url
    
if __name__=='__main__':
    print upload('/home/abhinav/librarian/librarian/boto_test.py', 'arastogi@stanford.edu', 'test1')
