import argparse
import os
import sys
import shutil
import glob


def copy_binaries(bin_root_path, arcgis_src_path):
    """
    Copy binaries for all platforms and python versions
    """
    BINARY_DESTINATIONS = {
        # In order to inject tracking-engine and knn, we need to resolve name collisions
        # i.e. update the filenames to include the python version
        # 'tracking-engine': 'learn/_tracking',
        # 'knn': 'learn/_utils'
        "nbauth": "gis/_impl",
        "graph": "graph",
    }
    binaries = _glob(bin_root_path, [".so", ".pyd"])
    for binary in binaries:
        dir = os.path.basename(
            os.path.dirname(binary)
        )  # gets the last folder of the binary file
        dest = BINARY_DESTINATIONS.get(dir)
        if not dest:
            continue
        print(f"{os.path.basename(binary)} -> {dest}/{os.path.basename(binary)}")
        dest = os.path.join(arcgis_src_path, dest)
        shutil.copy(binary, dest)


def clean_binaries(arcgis_src_path):
    """
    Removes binaries from source path
    """
    binaries = _glob(arcgis_src_path, [".so", ".pyd"])
    if len(binaries) == 0:
        print(f"No files to remove...")
        return
    for binary in binaries:
        print(f"Removing {binary}")
        os.remove(binary)


def _glob(path, extension):
    if isinstance(extension, list):
        _globbed = []
        for ext in extension:
            _globbed = _globbed + _glob(path, ext)
        return _globbed
    return glob.glob(os.path.join(path, f"**/*{extension}"), recursive=True)


def _get_argument_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="action", required=True)
    copy_parser = subparsers.add_parser("copy")
    copy_parser.add_argument(
        "--bin-path",
        action="store",
        help="Path of directory to inject pyd/so files",
        required=True,
    )
    copy_parser.add_argument(
        "--src-path",
        action="store",
        help="Path of directory to inject pyd/so files",
        required=True,
    )
    clean_parser = subparsers.add_parser("clean")
    clean_parser.add_argument(
        "--src-path",
        action="store",
        help="Path of directory to clean pyd/so files",
        required=True,
    )
    return parser


def _exit_if_path_not_exist(path):
    if isinstance(path, list):
        for p in path:
            _exit_if_path_not_exist(p)
        return
    if os.path.exists(path):
        return
    print(f"Couldn't find {path}")
    sys.exit(127)


if __name__ == "__main__":
    parser = _get_argument_parser()
    args = parser.parse_args()
    if args.action == "clean":
        _exit_if_path_not_exist(args.src_path)
        clean_binaries(args.src_path)
    elif args.action == "copy":
        _exit_if_path_not_exist([args.src_path, args.bin_path])
        copy_binaries(args.bin_path, args.src_path)