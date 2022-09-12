
def extract():
    import os
    import shutil
    
    home = os.path.expanduser("~")

    cache = os.path.join(home, '.cache')
    if os.path.exists(cache):
        shutil.rmtree(cache)

if __name__ == '__main__':
    extract()