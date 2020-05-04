def get_home_path():
    """ Function to return the home path irrespective of the OS. """
    import os
    home = os.curdir                      
    
    if 'HOME' in os.environ:
        home = os.environ['HOME']
    elif os.name == 'posix':
        home = os.path.expanduser("~/")
    elif os.name == 'nt':
        if 'HOMEPATH' in os.environ and 'HOMEDRIVE' in os.environ:
            home = os.environ['HOMEDRIVE'] + os.environ['HOMEPATH']
    else:
        home = os.environ['HOMEPATH']
    
    return home

def extract_zipfile(filepath, filename, remove=False):
    """ Function to extract the contents of a zip file
        Args:
            filepath: absolute path to the file directory.
            filename: name of the zip file to be extracted.
            remove: default=False, removes the original zip file 
                    after extracting the contents if True
    """
    import os, zipfile
    with zipfile.ZipFile(os.path.join(filepath, filename),"r") as zip_ref:
        zip_ref.extractall(filepath)
    if remove:
        os.remove(os.path.join(filepath, filename))