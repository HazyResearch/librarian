import boto
import boto.s3.connection
import os

access_key = os.getenv('AWS_KEY')
secret_key = os.getenv('AWS_SECRET_KEY')

conn = boto.s3.connection.S3Connection(
        aws_access_key_id = access_key,
        aws_secret_access_key = secret_key,
        # host = 'objects.dreamhost.com',
        # is_secure=False,               # uncomment if you are not using ssl
        calling_format = boto.s3.connection.OrdinaryCallingFormat(),
        )

bucket = conn.get_bucket('librarian_upload_test')
key = bucket.new_key('examples/third_file.txt')
key.set_contents_from_filename('/home/abhinav/Desktop/words.txt')
key.set_acl('public-read')
print key.generate_url(expires_in=0, query_auth=False)
print [k.name for k in bucket.list()]
print conn.get_all_buckets()
