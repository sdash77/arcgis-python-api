
def extract():
    import os
    import shutil
    
    home = os.path.expanduser("~")

    cache = os.path.join(home, '.cache')
    if not os.path.exists(cache):
        os.mkdir(cache)
    torch = os.path.join(cache, 'torch')
    if not os.path.exists(torch):
        os.mkdir(torch)
    weights = os.path.join(cache, 'weights')
    if not os.path.exists(weights):
        os.mkdir(weights)

    base_dir = os.path.dirname(os.path.abspath(__file__))

    shutil.unpack_archive(
        os.path.join(base_dir, 'torch.tar'), 
        torch
    )
    shutil.unpack_archive(
        os.path.join(base_dir, 'weights.tar'), 
        weights
    )

    os.remove(os.path.join(base_dir, 'torch.tar'))
    os.remove(os.path.join(base_dir, 'weights.tar'))

if __name__ == '__main__':
    extract()