import os

def list_files(directory):
    if os.path.isfile(directory):
        yield directory
        raise StopIteration
    for f in os.listdir(directory):
        name = directory + '/' + f
        if os.path.isfile(name):
            yield name
        elif os.path.isdir(name):
            for f in list_files(name):
                yield f
            
            
for f in list_files('/home/abhinav/Dropbox/github/librarian'):
    print f[len('/home/abhinav/Dropbox/github/librarian'):]
            
