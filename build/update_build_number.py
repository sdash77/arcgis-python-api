import os
import yaml, sys


def _apply_build_number_to_meta_yaml(build_number: int, meta_path: str):
    meta_yaml = {}
    with open(META_YAML_FILE_PATH, "r") as f:
        meta_yaml = yaml.load(f, Loader=yaml.FullLoader)
        meta_yaml["build"]["number"] = str(build_number)

    with open(META_YAML_FILE_PATH, "w") as f:
        yaml.dump(meta_yaml, f, default_flow_style=False, explicit_start=True)


#
## Inputs
#
# sys.argv[1] is the build number from the github action run
# sys.argv[2] is the relative path to the build file: ./arcgis/meta.yaml

build_number = sys.argv[1]
META_YAML_FILE_PATH = sys.argv[2]
print(build_number)
print(META_YAML_FILE_PATH)
#
## Update the meta.yaml file
#
_apply_build_number_to_meta_yaml(
    build_number=build_number, meta_path=META_YAML_FILE_PATH
)
