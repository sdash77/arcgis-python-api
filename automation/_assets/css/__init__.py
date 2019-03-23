import os
import glob

def get_css_asset_file_names():
    output = []
    this_dir = os.path.dirname(os.path.realpath(__file__))
    for g in glob.glob(os.path.join(this_dir, "*.css")):
        output.append(os.path.basename(g))
    return output
