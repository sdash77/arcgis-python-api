# Script using nbconvert and nbformat Python API to export Python API SDK material
import os, sys
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

#region read the command line args
parser = argparse.ArgumentParser()
parser.add_argument('input_path', help="Enter path to folder with guide or sample notebooks")
parser.add_argument('-o','--output_path', help="Enter path to store html files")
parser.add_argument('-e','--embed_tryitlive', help="Embed Try it live button? Simply call this option to set it to True",
                    action='store_true')

args = parser.parse_args()
root_path = args.input_path
if args.output_path:
    output_root_path = args.output_path
else:
    output_root_path = root_path
embed = args.embed_tryitlive
#endregion

unsafe_dirs = ['apidoc','labs','talks','data']

def rename_folders(root_path):
    """
    Renames folders.
    :param root_path:
    :return:
    """
    print("Renaming folders")
    print("--------------------------------------------------------------------------")

    # safety check first - check if you are renaming files or folders in unsafe places
    if True in list(map(lambda arg: arg in root_path, unsafe_dirs)):
        print("    safety check. Skipping ")
        return

    #loop through all dir and subdir
    for directory, subdir_list, file_list in os.walk(root_path):
        print(directory)

        #rename the folders
        for subd in subdir_list:
            if 'checkpoint' in subd: #ignore the ipynb checkpoints
                continue
            new_subd_name = subd.lower().replace(" ","-").replace("_","-")
            if new_subd_name != subd:
                os.rename(os.path.join(directory, subd), os.path.join(directory, new_subd_name))
                print("   renamed " + subd + " to " + new_subd_name)

def rename_files(root_path):
    """
    Renames files. Doing this separately, since if I rename folders and files in the same go,
    it might mess up with the system's list of folders and files.
    :param root_path:
    :return:
    """
    print("Renaming files")
    print("--------------------------------------------------------------------------")

    # safety check first - check if you are renaming files or folders in unsafe places
    if True in list(map(lambda arg: arg in root_path, unsafe_dirs)):
        print("    safety check. Skipping ")
        return

    #loop through all dir and subdir
    for directory, subdir_list, file_list in os.walk(root_path):
        print(directory)

        #rename the files.
        for curr_file in fnmatch.filter(file_list, "*.ipynb"):
            new_file_name = curr_file.lower().replace(" ","-").replace("_","-")
            if new_file_name != curr_file:
                os.rename(os.path.join(directory, curr_file), os.path.join(directory, new_file_name))
                print("   renamed " + curr_file + " to " + new_file_name)

def export_notebooks(root_path, output_root_path, embed_try_it_live=False):
    """
    export Jupyter Notebooks in basic HTML. Will not execute the notebook. All html files will be stored in same folder.
    Since this is the pattern for files on developers.arcgis.com
    :param root_path:
    :param output_root_path:
    :return:
    """
    print("Exporting notebooks to html")
    print("--------------------------------------------------------------------------")

    #region safety check first - check if you are renaming files or folders in unsafe places
    if True in list(map(lambda arg: arg in root_path, unsafe_dirs)):
        print("    safety check. Skipping ")
        return
    #endregion

    for directory, subdir_list, file_list in os.walk(root_path):
        print(directory)

        #loop ipynb files.
        for curr_file in fnmatch.filter(file_list, "*.ipynb"):
            if 'checkpoint' in curr_file: #dont bother with checkpoint files.
                continue

            print("    Converting " + curr_file, end=" ")
            try:
                #region nbconvert notebook
                html_exporter = HTMLExporter()
                html_exporter.template_file = 'basic'

                (body, resources) = html_exporter.from_filename(os.path.join(directory,curr_file))
                print("| exported ", end=" ")
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
                print("| made title ", end=" ")
                #endregion

                #region inject try-it-live link
                # there is probably a better way, namely registering this as a
                # custom processer in nbconvert and injecting using bs4 elements. We can improve this later.
                if embed_try_it_live:
                    curr_folder = os.path.split(directory)[-1]

                    button_html = '<div align="right">'
                    button_html = button_html+ '<a class="btn" href="/python/sample-notebooks/#Download-and-run-the-sample-notebooks">' + \
                                    'Download the samples</a>'
                    button_html = button_html +" "+ '<a class="btn" href="//notebooks.esri.com/notebooks/samples/' + curr_folder + \
                                  r'/' + curr_file + '" target="_blank"> Try it live </a>'
                    button_html = button_html + "</div>"
                else:
                    button_html = ""
                print("| made button ", end=" ")
                #endregion

                #region write to disk
                web_safe_curr_file = os.path.splitext(curr_file)[0].replace(".","-")
                output_file_name = os.path.join(output_root_path, web_safe_curr_file + ".html")
                with open(output_file_name, 'wb') as html_file_handle:
                    all_str =header_str + button_html + body
                    html_file_handle.write(all_str.encode("utf-8"))
                #endregion
                print("| wrote to disk.")

            except Exception as convert_ex:
                print(str(convert_ex))
                continue

if __name__ == '__main__':
    rename_folders(root_path)
    rename_files(root_path)
    export_notebooks(root_path, output_root_path, embed)
    # print(root_path)
    # print(output_root_path)
    # print(embed)