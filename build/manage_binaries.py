import argparse
import os
import sys
import shutil
import glob
import requests

PYTHON_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}"


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
    binaries = _glob(bin_root_path, [".so", ".dll", ".pyd"])
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


def download_binaries(
    python_version, arcgis_version, arcgis_src_path, mode, conda_platform
):
    def expand_urls(module, files_by_platform):
        return {
            platform: [
                f"https://esri-forge.python.geocloud.com/_/build/v{arcgis_version}/{platform}/py{python_version}/{module}/{file}"
                for file in files
            ]
            for platform, files in files_by_platform.items()
        }

    def download_file(url, dest):
        print(f"{url} -> {dest}")
        with requests.get(url, stream=True) as r:
            try:
                r.raise_for_status()
                with open(os.path.join(dest, os.path.basename(url)), "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            except:
                # .py files are optional on some platforms, ok to skip
                if not os.path.splitext(url)[1] == ".py":
                    raise

    def download_files(urls, dest):
        for url in urls:
            download_file(url, dest)

    python_version_stripped = python_version.replace(".", "")  # e.g. 3.11 => 311

    if mode == "conda":
        knn_dest = os.path.join(arcgis_src_path, "learn/_utils")
        os.makedirs(knn_dest, exist_ok=True)
        knn_files = expand_urls(
            "knn",
            {
                "linux": [
                    "nearest_neighbors.py",
                    f"nearest_neighbors.cpython-{python_version_stripped}-x86_64-linux-gnu.so",
                ],
                "windows": [
                    "nearest_neighbors.py",
                    f"nearest_neighbors.cp{python_version_stripped}-win_amd64.pyd",
                ],
            },
        )
        download_files(knn_files[conda_platform], knn_dest)

        tracking_engine_dest = os.path.join(arcgis_src_path, "learn/_tracking")
        os.makedirs(tracking_engine_dest, exist_ok=True)
        tracking_engine_files = expand_urls(
            "tracking-engine",
            {
                "linux": ["_track_processor.so", "libTrackingEngine.so"],
                "windows": ["_track_processor.pyd", "tracking_engine.dll"],
            },
        )
        download_files(tracking_engine_files[conda_platform], tracking_engine_dest)

    graph_dest = os.path.join(arcgis_src_path, "graph")
    os.makedirs(graph_dest, exist_ok=True)
    graph_files = expand_urls(
        "graph",
        {
            "linux": [
                f"_arcgisknowledge.cpython-{python_version_stripped}-x86_64-linux-gnu.so"
            ],
            "windows": [
                f"_arcgisknowledge.cpython-{python_version_stripped}-win_amd64.pyd"
            ],
        },
    )
    download_files(
        (
            graph_files[conda_platform]
            if mode == "conda"
            else graph_files["windows"] + graph_files["linux"]
        ),
        graph_dest,
    )

    nbauth_dest = os.path.join(arcgis_src_path, "gis/_impl")
    os.makedirs(nbauth_dest, exist_ok=True)
    nbauth_files = expand_urls(
        "nbauth",
        {
            "linux": [
                f"_decrypt_nbauth.cpython-{python_version_stripped}-x86_64-linux-gnu.so"
            ],
            "windows": [f"_decrypt_nbauth.cp{python_version_stripped}-win_amd64.pyd"],
        },
    )
    download_files(
        (
            nbauth_files[conda_platform]
            if mode == "conda"
            else nbauth_files["windows"] + nbauth_files["linux"]
        ),
        nbauth_dest,
    )


def clean_binaries(arcgis_src_path):
    """
    Removes binaries from source path
    """
    binaries = _glob(arcgis_src_path, [".so", ".dll", ".pyd"])
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
        help="Path of directory to inject pyd/so files. If not provided, binaries will be downloaded.",
        required=False,
    )
    copy_parser.add_argument(
        "--arcgis",
        action="store",
        help="arcgis version to download binaries for",
        required=True,
    )
    copy_parser.add_argument(
        "--python",
        action="store",
        help="Python version to download binaries for",
        required=False,
        default=PYTHON_VERSION,
    )
    copy_parser.add_argument(
        "--src-path",
        action="store",
        help="Path of directory to inject pyd/so files",
        required=True,
    )
    copy_parser.add_argument(
        "--linux",
        action="store_true",
        help="Download linux binaries",
        default=os.name == "posix",
    )
    copy_parser.add_argument(
        "--windows",
        action="store_true",
        help="Download windows binaries",
        default=os.name != "posix",
    )
    copy_parser.add_argument(
        "--conda",
        "--test",
        "--local",
        dest="conda",
        action="store_true",
        help="Download binaries for conda build/automated testing/local development",
        default=False,
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
    _exit_if(not os.path.exists(path), f"Couldn't find {path}")


def _exit_if(condition, message):
    if not condition:
        return
    print(message)
    sys.exit(127)


def _validate_args(args):
    if args.action == "copy":
        if args.bin_path:
            _exit_if_path_not_exist(args.bin_path)
        _exit_if_path_not_exist(args.src_path)
        _exit_if(
            args.conda and not args.linux and not args.windows,
            "One of --linux or --windows must be set when using --conda",
        )
    if args.action == "clean":
        _exit_if_path_not_exist(args.src_path)


if __name__ == "__main__":
    parser = _get_argument_parser()
    args = parser.parse_args()
    _validate_args(args)
    if args.action == "clean":
        _exit_if_path_not_exist(args.src_path)
        clean_binaries(args.src_path)
    elif args.action == "copy":
        if args.bin_path:
            copy_binaries(args.bin_path, args.src_path)
        else:
            download_binaries(
                args.python,
                args.arcgis,
                args.src_path,
                "conda" if args.conda else "pip",
                "linux" if args.linux else "windows",
            )
