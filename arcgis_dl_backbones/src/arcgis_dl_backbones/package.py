
def package():
    import os
    import shutil
    
    home = os.path.expanduser("~")

    cache = os.path.join(home, '.cache')
    torch = os.path.join(cache, 'torch')
    weights = os.path.join(cache, 'weights')

    # SP_DIR env variable is only available in conda-build 
    shutil.make_archive(
        os.path.join(os.environ['SP_DIR'], 'arcgis_dl_backbones', 'torch'), 
        'tar', 
        base_dir=None, 
        root_dir=torch
    )
    shutil.make_archive(
        os.path.join(os.environ['SP_DIR'], 'arcgis_dl_backbones', 'weights'), 
        'tar', 
        base_dir=None, 
        root_dir=weights
    )


if __name__ == '__main__':
    package()