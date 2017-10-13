import os

from __init__ import BUILD_DIR

def build_conda_package():
    if os.name == 'posix':
        raise RuntimeError("Conda building not supported on *nix systems")
    elif os.name == 'nt':
        _build_conda_for_windows()
    else:
        raise RuntimeError("Conda building not supported on this platform")

    print("Conda building finished! Any results in {}".format(
        os.path.join(GEOSAURUS_ROOT_DIR, 'automation', 'staging')))

def _build_conda_for_windows():
    print("Building for Windows system...")
    bat_build_command = "buildarcgis"
    flag_to_force_output_to_staging_dir = STAGING_DIR
    final_make_command = 'cd "{}" && {} {}'.format(
            BUILD_DIR,
            bat_build_command,
            flag_to_force_output_to_staging_dir)

    _run_sys_command(final_make_command)

def _run_sys_command(cmd):
    print("About to run the following command: '{}'".format(cmd))
    subprocess.check_call(cmd, shell=True)

if __name__ == "__main__":
    build_conda_package()
