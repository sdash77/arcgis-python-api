import os
import sys
import shutil
import platform


def clean_up_unneeded_files(path):
    """
    Removes unneeded .so/.pyd files for each build

    This will delete the .so/.pyd plus extra directories for the compiled code.
    The so/pyd files add additional size to the package and reducing it will make packages smaller.

    The following files will be erased:

       - _arcgisknowledge.pyd
       - _arcgisknowledge.so
       - _decrypt_nbauth.cpython-<python version>-x86_64-linux-gnu.<extension>

    """
    pyversion = "%s%s" % (sys.version_info.major, sys.version_info.minor)
    for_python = "for_python%s%s" % (sys.version_info.major, sys.version_info.minor)
    if platform.system().lower().find("windows") > -1:
        extra_ext = ".so"
    else:
        extra_ext = ".pyd"

    exts = ('.so', '.pyd')
    delete_files = set()
    delete_folders = set()
    for root, dirs, files in os.walk(path):
        for currentFile in files:
            # print("processing file: " + currentFile)
            fp = os.path.join(root, currentFile)
            if currentFile.lower().endswith(exts) and fp.lower().find(pyversion) == -1:
                delete_files.add(fp)
            elif (
                currentFile.lower().endswith(extra_ext)
                and fp.lower().find(pyversion) > -1
            ):
                delete_files.add(fp)
            if (
                os.path.dirname(fp).lower().find("for_python") > -1
                and fp.find(for_python) == -1
            ):
                delete_folders.add(os.path.dirname(fp))
    for f in delete_files:
        os.remove(f)
    for d in delete_folders:
        shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    path = str(sys.argv[1]).strip()
    clean_up_unneeded_files(path)
