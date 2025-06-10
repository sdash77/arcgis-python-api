import argparse
import os
import sys
import shutil
import glob
import requests


def get_version(init_file_path):
    def discard_subpatch_version(version):
        "Returns the full version with the subpatch version discarded (i.e. MAJOR.MINOR.PATCH, if MAJOR.MINOR.PATCH.SUBPATCH provided)"
        return ".".join(version.split(".")[:3])

    try:
        with open(init_file_path, "r") as f:
            init_file = f.read()
        for line in init_file.splitlines():
            if line.startswith("__version__"):
                delim = '"' if '"' in line else "'"
                return discard_subpatch_version(line.split(delim)[1])
    except:
        pass
    return None


SRC_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "src", "arcgis")
)
PYTHON_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}"
ARCGIS_VERSION = get_version(os.path.join(SRC_PATH, "__init__.py"))
PIP_PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13"]
LEARN_PYTHON_VERSIONS = ["3.10", "3.11"]


def copy_binaries(bin_root_path, arcgis_src_path):
    """
    Copy binaries for all platforms and python versions
    """
    BINARY_DESTINATIONS = {
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
    python_versions, arcgis_version, arcgis_src_path, mode, conda_platform
):
    def expand_urls(module, file_funcs_by_platform):
        def get_python_version_stripped(python_version):
            return python_version.replace(".", "")

        return {
            platform: [
                f"https://esri-forge.python.geocloud.com/_/build/v{arcgis_version}/{platform}/py{python_version}/{module}/{file_func(get_python_version_stripped(python_version))}"
                for file_func in file_funcs
                for python_version in python_versions
            ]
            for platform, file_funcs in file_funcs_by_platform.items()
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

    if mode == "conda" and all(
        python_version in LEARN_PYTHON_VERSIONS for python_version in python_versions
    ):
        knn_dest = os.path.join(arcgis_src_path, "learn/_utils")
        os.makedirs(knn_dest, exist_ok=True)
        knn_files = expand_urls(
            "knn",
            {
                "linux": [
                    lambda _: "nearest_neighbors.py",
                    lambda python_version_stripped: f"nearest_neighbors.cpython-{python_version_stripped}-x86_64-linux-gnu.so",
                ],
                "windows": [
                    lambda _: "nearest_neighbors.py",
                    lambda python_version_stripped: f"nearest_neighbors.cp{python_version_stripped}-win_amd64.pyd",
                ],
            },
        )
        download_files(knn_files[conda_platform], knn_dest)

        tracking_engine_dest = os.path.join(arcgis_src_path, "learn/_tracking")
        os.makedirs(tracking_engine_dest, exist_ok=True)
        tracking_engine_files = expand_urls(
            "tracking-engine",
            {
                "linux": [
                    lambda _: "_track_processor.so",
                    lambda _: "libTrackingEngine.so",
                ],
                "windows": [
                    lambda _: "_track_processor.pyd",
                    lambda _: "tracking_engine.dll",
                ],
            },
        )
        download_files(tracking_engine_files[conda_platform], tracking_engine_dest)
    elif mode == "conda":
        print(
            "Skipping arcgis_learn binaries, python version not supported.  If Local, automated tests may fail."
        )

    graph_dest = os.path.join(arcgis_src_path, "graph")
    os.makedirs(graph_dest, exist_ok=True)
    graph_files = expand_urls(
        "graph",
        {
            "linux": [
                lambda python_version_stripped: f"_arcgisknowledge.cpython-{python_version_stripped}-x86_64-linux-gnu.so"
            ],
            "windows": [
                lambda python_version_stripped: f"_arcgisknowledge.cp{python_version_stripped}-win_amd64.pyd"
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
    parser = argparse.ArgumentParser(
        description="Manage arcgis dependent binaries (such as knn and knowledge]graph) in your environment.",
        epilog="Sample usage for local development: %(prog)s copy --local",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    copy_parser = subparsers.add_parser(
        "copy", epilog="Sample usage: %(prog)s copy --local"
    )
    copy_parser.add_argument(
        "--bin-path",
        action="store",
        help="Path of directory to inject pyd/so files. If not provided, binaries will be downloaded.",
        required=False,
    )
    copy_parser.add_argument(
        "--arcgis",
        action="store",
        help=(
            f"arcgis version to download binaries for [default: {ARCGIS_VERSION}]"
            "\nNOTE: Default value only uses MAJOR.MINOR.PATCH version. If you need to "
            "patch binaries for a subpatch version (e.g. MAJOR.MINOR.PATCH.SUBPATCH), "
            "you must provide the full version with this argument."
        ),
        required=not bool(ARCGIS_VERSION),
        default=ARCGIS_VERSION,
    )
    copy_parser.add_argument(
        "--python",
        action="store",
        help=f"Python version to download binaries for [default: {PYTHON_VERSION}]",
        required=False,
        default=PYTHON_VERSION,
    )
    copy_parser.add_argument(
        "--src-path",
        action="store",
        help=f"Path of directory to inject pyd/so files\n[default: {SRC_PATH}]",
        required=not os.path.exists(SRC_PATH),
        default=SRC_PATH,
    )
    copy_parser.add_argument(
        "--linux",
        "--macos",
        dest="linux",
        action="store_true",
        help=f"Download linux binaries [default: {os.name == 'posix'}]",
        default=os.name == "posix",
    )
    copy_parser.add_argument(
        "--windows",
        action="store_true",
        help=f"Download windows binaries [default: {os.name != 'posix'}]",
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
        required=False,
        default=SRC_PATH,
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
                [args.python] if args.conda else PIP_PYTHON_VERSIONS,
                args.arcgis,
                args.src_path,
                "conda" if args.conda else "pip",
                "linux" if args.linux else "windows",
            )
