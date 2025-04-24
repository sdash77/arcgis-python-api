import sys
from pathlib import Path
import unittest
import arcpy
import os
import stat
import shutil
import warnings
warnings.filterwarnings("ignore")

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

ARCGIS_FOLDER = os.environ.get('ARCGIS_FOLDER')
if ARCGIS_FOLDER:
    custom_arcgis_path = Path(ARCGIS_FOLDER)
    if str(custom_arcgis_path) not in sys.path:
        sys.path.insert(0, str(custom_arcgis_path))
else:
    print("Warning: ARCGIS_FOLDER environment variable is not set.")


import arcgis
from inference_properties import (
    data_inferencing,
    input_data_path_ms,
    input_data_path_rgb,
    output_gdb_folder,
    saved_models_path,
    output_gdb,
)
from parameterized import parameterized

file_gdb_path = os.path.join(output_gdb_folder, output_gdb)

def pixelClassification_params_rgb():
    is_ms = False
    parameter = []
    for key, val in data_inferencing.items():
        if (val["should_test"] and val["inference_function"] == "ClassifyPixelsUsingDeepLearning"):
            parameter.append(
                (
                    key,
                    val["input_path_rgb"],
                    val["model_path_rgb"],
                    os.path.join(output_gdb_folder, output_gdb, val["output_filename_rgb"]),
                    val["padding"],
                    val["batch_size"],
                    val["threshold"],
                    os.path.join(output_gdb_folder, output_gdb),
                )
            )
    return parameter


def pixelClassification_params_ms():
    is_ms = True
    parameter = []
    for key, val in data_inferencing.items():
        if (val["should_test"] and val["inference_function"] == "ClassifyPixelsUsingDeepLearning" and val["input_path_ms"] != False):
            parameter.append(
                (
                    key+"_ms",
                    val["input_path_ms"],
                    val["model_path_ms"],
                    os.path.join(output_gdb_folder, output_gdb, val["output_filename_ms"]),
                    val["padding"],
                    val["batch_size"],
                    val["threshold"],
                    os.path.join(output_gdb_folder, output_gdb),
                )
            )
    return parameter

def pixelClassificationInferencing(name, input_image_path, model, output_file_path, padding, batch_size, threshold, scratch_workspace):
    print("Running Inferencing for:", name)
    with arcpy.EnvManager(scratchWorkspace=scratch_workspace):
        out_classified_raster = arcpy.ia.ClassifyPixelsUsingDeepLearning(
            in_raster=input_image_path,
            in_model_definition=model,
            arguments=f"padding {padding};batch_size {batch_size};return_probability_raster False;threshold {threshold};test_time_augmentation False;merge_policy max;tile_size 128",
            processing_mode="PROCESS_AS_MOSAICKED_IMAGE",
            out_classified_folder=None,
            out_featureclass=None,
            overwrite_attachments="NO_OVERWRITE",
            use_pixelspace="NO_PIXELSPACE"
        )
        out_classified_raster.save(output_file_path)


class TestInferencing(unittest.TestCase):

    @parameterized.expand(pixelClassification_params_rgb)
    def test_pixelClassification(
        self,
        name,
        input_image_path,
        model,
        output_file_path,
        padding,
        batch_size,
        threshold,
        scratch_workspace,
    ):
        pixelClassificationInferencing(name, input_image_path, model, output_file_path, padding, batch_size, threshold, scratch_workspace)


    @parameterized.expand(pixelClassification_params_ms)
    def test_pixelClassification_ms(
        self,
        name,
        input_image_path,
        model,
        output_file_path,
        padding,
        batch_size,
        threshold,
        scratch_workspace,
    ):
        pixelClassificationInferencing(name, input_image_path, model, output_file_path, padding, batch_size, threshold, scratch_workspace)


    @classmethod
    def setUpClass(cls):
        if os.path.exists(file_gdb_path):
            print("The geodatabase already exists at: ", file_gdb_path)
            print("Deleting existing file geodatabase")
            shutil.rmtree(file_gdb_path)
            print("Deleted old geodatabase successfully")
            print("creating new file geodatabase")
            arcpy.CreateFileGDB_management(output_gdb_folder, output_gdb)
            print("File geodatabase created successfully")
        else:
             print("creating new file geodatabase")
             arcpy.CreateFileGDB_management(output_gdb_folder, output_gdb)
             print("File geodatabase created successfully")
            
    
    @classmethod
    def tearDownClass(cls):
        print("Test cases completed successfully")


if __name__ == "__main__":
    unittest.main()
