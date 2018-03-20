# Script using nbconvert and nbformat Python API to export Python API SDK material
import os, sys
import logging
log = logging.getLogger()

try:
    from traitlets.config import Config
    from nbconvert import HTMLExporter
    from bs4 import BeautifulSoup
except ImportError as ie:
    print(str(ie))
    print("Required libs not present. Quitting")
    exit(1)
import fnmatch
import argparse

unsafe_dirs = ['apidoc','labs','talks','data']
DEFAULT_IMG_PREFIX = "/assets/img/python-graphics/" #What the dev site uses

def _parse_args():
    #region read the command line args
    parser = argparse.ArgumentParser()
    parser.add_argument('input_path', help="Enter path to folder with guide or sample notebooks")
    parser.add_argument('-o','--output_path', help="Enter path to store html files", required=True)
    parser.add_argument('-e','--embed_tryitlive', help="Embed Try it live button? Simply call this option to set it to True",
                       action='store_true')
    parser.add_argument('-r', '--replace-img-path', help="Replace all relative image paths with what is defined in --img-prefix?",
                        action='store_true', default=False)
    parser.add_argument('-i', '--img-prefix', help="The prefix path to put before all images if -r specified (Default {})".format(DEFAULT_IMG_PREFIX),
                        default=DEFAULT_IMG_PREFIX)
    return parser.parse_args()

def export_notebooks(root_path, output_root_path, embed_try_it_live=False,
        replace_img_path=False, img_prefix=DEFAULT_IMG_PREFIX):
    """
    export Jupyter Notebooks in basic HTML. Will not execute the notebook. All html files will be stored in same folder.
    Since this is the pattern for files on developers.arcgis.com
    :param root_path:
    :param output_root_path:
    :param replace_img_path:
    :param img_prefix:
    :return:
    """
    log.info("Exporting notebooks to html")
    log.info("--------------------------------------------------------------------------")

    #region safety check first - check if you are renaming files or folders in unsafe places
    if True in list(map(lambda arg: arg in root_path, unsafe_dirs)):
        log.info("    safety check. Skipping ")
        return
    #endregion

    for directory, subdir_list, file_list in os.walk(root_path):
        log.info(directory)

        #loop through all .ipynb files, skipping checkpoints.
        for curr_file in fnmatch.filter(file_list, "*.ipynb"):
            if 'checkpoint' in curr_file:
                continue
            log_str = "\tConverting " + curr_file

            #Try the actual conversion now, pass any unhandled exception
            try:
                #region nbconvert notebook
                html_exporter = HTMLExporter()
                html_exporter.template_file = 'basic'
                (body, resources) = html_exporter.from_filename(os.path.join(directory,curr_file))
                log_str += " | exported "
                #endregion

                #region inject title and SEO stuff into the html
                soup = BeautifulSoup(body, 'html.parser')
                header_str = "---"
                try:
                    #try to get the heading. If not, unparse the file name to construct the title.
                    hit_heading = soup.find('h1')
                    title = hit_heading.contents[0]
                except:
                    title = curr_file.split(".")[0].replace("-", " ")
                header_str = header_str + "\ntitle: " + title + "\n---\n\n"
                log_str += " | made title "
                #endregion

                #region replace all relative path img srcs with the dev-site format
                if replace_img_path:
                    for img in soup.findAll('img'):
                        if "http" not in img["src"]:
                        #Will match with all relative paths in the notebook
                            filename = img["src"].split("/")[-1]
                            img["src"] = img_prefix + filename
                    log_str += " | modified img "
                #end region

                #region inject try-it-live link
                if embed_try_it_live:
                    button_html = _get_button_html(directory)
                else:
                    button_html = ""
                log_str += " | made button "
                #endregion

                #region write to disk                
                output_file_name = _get_output_file_name(curr_file)
                output_file_path = os.path.join(output_root_path, output_file_name)
                with open(output_file_path, 'wb') as html_file_handle:
                    all_str = header_str + button_html + str(soup)
                    html_file_handle.write(all_str.encode("utf-8"))
                log_str += " | wrote to disk."
                #endregion

                #Print that log string that's been accumulating info so far
                log.info(log_str)

            except Exception as convert_ex:
                print(str(convert_ex))
                continue

def _get_button_html(directory):
    """Gets the html str of the 'try it live' button.
     There is probably a better way, namely registering this as a
     custom processer in nbconvert and injecting using bs4 elements. We can improve this later.
    """
    curr_folder = os.path.split(directory)[-1]

    button_html = '<div align="right">'
    button_html = button_html+ '<a class="btn" href="/python/sample-notebooks/#Download-and-run-the-sample-notebooks">' + \
                               'Download the samples</a>'
    button_html = button_html +" "+ '<a class="btn" href="//notebooks.esri.com/notebooks/samples/' + curr_folder + \
                               r'/' + curr_file + '" target="_blank"> Try it live </a>'
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
    logging.basicConfig(level=logging.INFO)
    args = _parse_args()
    export_notebooks(args.input_path,
                     args.output_path,
                     args.embed_tryitlive,
                     args.replace_img_path,
                     args.img_prefix)
