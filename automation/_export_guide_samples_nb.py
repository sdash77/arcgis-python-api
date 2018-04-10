info_text = """
This script used to live in geosaurus/build/bld_sdk/, until it was improved
upon & integrated with the new system that now lives in this automation folder.

All logic in this file is called from stage_notebooks_for_dev_web_repo.py:
THIS FILE SHOULD NOT BE CALLED DIRECTLY IN ANY WAY. Please use
geosaurus/build/notebook_to_dev_site, there is a README.md in that dir that 
explains everything
"""
# Script using nbconvert and nbformat to convert notebooks to html
import os
import sys
import fnmatch
import logging
log = logging.getLogger()

from traitlets.config import Config
from nbconvert import HTMLExporter
from bs4 import BeautifulSoup

unsafe_dirs = ['apidoc','labs','talks','data']
DEFAULT_IMG_PREFIX = "/assets/img/python-graphics/" #What the dev site uses

def export_notebooks(root_path, output_root_path, embed_try_it_live=False,
                     replace_img_path=False, img_prefix=DEFAULT_IMG_PREFIX,
                     log_func=log.info):
    f"""
    export Jupyter Notebooks in basic HTML. Will not execute the notebook.
    {info_text}
    :param root_path: notebooks root dir (normally arcgis-python-api repo)
    :param output_root_path: html output root (normally arcgis-for-dev repo)
    :param replace_img_path:
    :param img_prefix:
    :return:
    """
    log_func(f"Converting notebooks at {root_path} to html, placing output "\
             f"in {output_root_path}")

    #check if you are renaming files or folders in 'unsafe_dirs'
    if True in list(map(lambda arg: arg in root_path, unsafe_dirs)):
        log_func("ATTEMPTING TO CONVERT NOTEBOOKS IN DESIGNATED 'unsafe_dirs'"\
                 f". Skipping these notebooks. unsafe_dirs = {unsafe_dirs}")
        return
    #endregion

    #loop through all files in the root_path
    for directory, subdir_list, file_list in os.walk(root_path):
        log_func(directory)

        #loop through all .ipynb files
        for curr_file in fnmatch.filter(file_list, "*.ipynb"):
            #region skip checkpoints
            if 'checkpoint' in curr_file:
                continue
            log_str = "\tConverting " + curr_file
            #endregion

            #region nbconvert notebook
            html_exporter = HTMLExporter()
            html_exporter.template_file = 'basic'
            (body, resources) = html_exporter.from_filename(
                    os.path.join(directory,curr_file))
            log_str += " | exported "
            #endregion

            #region inject title and SEO stuff into the html
            soup = BeautifulSoup(body, 'html.parser')
            header_str = "---"
            try:
                #try to get the heading.
                hit_heading = soup.find('h1')
                title = hit_heading.contents[0]
            except Exception as e:
                #If not, unparse the file name to construct the title.
                title = curr_file.split(".")[0].replace("-", " ")
            header_str = header_str + "\ntitle: " + title + "\n---\n\n"
            log_str += " | made title "
            #endregion

            #region replace all rel path img srcs with the dev-site format
            if replace_img_path:
                for img in soup.findAll('img'):
                    if ("http" not in img["src"]) and \
                       ("data:" not in img["src"]):
                        #Will match with all relative paths in the notebook
                        filename = img["src"].split("/")[-1]
                        img["src"] = img_prefix + filename
                log_str += " | modified img "
            #end region

            #region inject try-it-live link
            if embed_try_it_live:
                button_html = _get_button_html(directory, curr_file)
            else:
                button_html = ""
            log_str += " | made button "
            #endregion

            #region write to disk                
            output_file_name = _get_output_file_name(curr_file)
            output_file_path = os.path.join(output_root_path,
                                            output_file_name)
            with open(output_file_path, 'wb') as html_file_handle:
                all_str = header_str + button_html + str(soup)
                html_file_handle.write(all_str.encode("utf-8"))
            log_str += " | wrote to disk."
            #endregion

            #Print that log string that's been accumulating info so far
            log_func(log_str)

def _get_button_html(directory, curr_file):
    """Gets the html str of the 'try it live' button.
     There is probably a better way, namely registering this as a
     custom processer in nbconvert and injecting using bs4 elements.
     We can improve upon this later
    """
    curr_folder = os.path.split(directory)[-1]

    button_html = '<div align="right">'
    button_html = button_html + ""\
        '<a class="btn" href="/python/sample-notebooks/'\
            '#Download-and-run-the-sample-notebooks">' + \
        'Download the samples</a>'
    button_html = button_html + " " + \
        '<a class="btn" href="https://notebooks.esri.com/notebooks/samples/'\
        "" + curr_folder + r'/' + curr_file + ""\
        '" target="_blank"> Try it live </a>'
    button_html = button_html + "</div>"
    return button_html 

def _get_output_file_name(file_name):
    """Replaces all underscores '_' and spaces ' ' with dashes '-'.
    Replaces '.ipynb' extension with '.html'
    """
    output_file_name = file_name.split(".")[0]
    output_file_name = output_file_name.replace(" ", "-")
    output_file_name = output_file_name.replace("_", "-")
    output_file_name = output_file_name + ".html"
    return output_file_name

if __name__ == '__main__':
    print(info_text)
    exit(1)
