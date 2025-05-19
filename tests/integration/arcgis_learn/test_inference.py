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
                    val["model_args"],
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
                    val["model_args"],
                    os.path.join(output_gdb_folder, output_gdb),
                )
            )
    return parameter


def objectDetection_params_rgb():
    is_ms = False
    parameter = []
    for key, val in data_inferencing.items():
        if (val["should_test"] and val["inference_function"] == "DetectObjectsUsingDeepLearning"):
            parameter.append(
                (
                    key,
                    val["input_path_rgb"],
                    val["model_path_rgb"],
                    os.path.join(output_gdb_folder, output_gdb, val["output_filename_rgb"]),
                    val["model_args"],
                )
            )
    return parameter


def objectDetection_params_ms():
    is_ms = True
    parameter = []
    for key, val in data_inferencing.items():
        if (val["should_test"] and val["inference_function"] == "DetectObjectsUsingDeepLearning" and val["input_path_ms"] != False):
            parameter.append(
                (
                    key+"_ms",
                    val["input_path_ms"],
                    val["model_path_ms"],
                    os.path.join(output_gdb_folder, output_gdb, val["output_filename_ms"]),
                    val["model_args"],
                )
            )
    return parameter


def detection3d_params():
    parameter = []
    for key, val in data_inferencing.items():
        if (val["should_test"] and val["inference_function"] == "DetectObjectsFromPointCloudUsingTrainedModel"):
            parameter.append(
                (
                    key,
                    val["input_path"],
                    val["model_path"],
                    os.path.join(output_gdb_folder, output_gdb, val["output_filename"]),
                    val["batch_size"],
                )
            )
    return parameter


def classification3d_params():
    parameter = []
    for key, val in data_inferencing.items():
        if (val["should_test"] and val["inference_function"] == "ClassifyPointCloudUsingTrainedModel"):
            parameter.append(
                (
                    key,
                    val["input_path"],
                    val["model_path"],
                    val["batch_size"],
                )
            )
    return parameter


def pixelClassificationInferencing(name, input_image_path, model, output_file_path, model_args, scratch_workspace):
    print("Running Inferencing for:", name)
    if name == 'psetae':
        with arcpy.EnvManager(extent='-120.464378740435 37.0061333692514 -120.416723873971 37.0509788876926 GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]', scratchWorkspace=scratch_workspace):
            out_classified_raster = arcpy.ia.ClassifyPixelsUsingDeepLearning(
            in_raster=input_image_path,
            in_model_definition=model,
            arguments=model_args,
            processing_mode="PROCESS_AS_MOSAICKED_IMAGE",
            out_classified_folder=None,
            out_featureclass=None,
            overwrite_attachments="NO_OVERWRITE",
            use_pixelspace="NO_PIXELSPACE"
        )
        out_classified_raster.save(output_file_path)
    else:
        with arcpy.EnvManager(scratchWorkspace=scratch_workspace):
            out_classified_raster = arcpy.ia.ClassifyPixelsUsingDeepLearning(
            in_raster=input_image_path,
            in_model_definition=model,
            arguments=model_args,
            processing_mode="PROCESS_AS_MOSAICKED_IMAGE",
            out_classified_folder=None,
            out_featureclass=None,
            overwrite_attachments="NO_OVERWRITE",
            use_pixelspace="NO_PIXELSPACE"
        )
        out_classified_raster.save(output_file_path)


def objectDetectionInferencing(name, input_image_path, model, output_file_path,  model_args):
    print("Running Inferencing for:", name)
    with arcpy.EnvManager(scratchWorkspace=r""):
        arcpy.ia.DetectObjectsUsingDeepLearning(
            in_raster=input_image_path,
            out_detected_objects=output_file_path,
            in_model_definition=model,
            arguments=model_args,
            run_nms="NO_NMS",
            confidence_score_field="Confidence",
            class_value_field="Class",
            max_overlap_ratio=0,
            processing_mode="PROCESS_AS_MOSAICKED_IMAGE",
            use_pixelspace="NO_PIXELSPACE",
            in_objects_of_interest=None
        )

def detection3dInferencing(name, input_path, model, output_file_path, batch_size):
    print("Running inference for: ", name)
    arcpy.ddd.DetectObjectsFromPointCloudUsingTrainedModel(
    in_point_cloud=input_path,
    in_trained_model=model,
    target_objects="1 0.5 0.2",
    out_features=output_file_path,
    batch_size=batch_size,
    boundary=None,
    reference_height=None,
    excluded_class_codes=[]
)


def classification3dInferencing(name, input_path, model, batch_size):
    print("Running inference for: ", name)
    arcpy.ddd.ClassifyPointCloudUsingTrainedModel(
    in_point_cloud=input_path,
    in_trained_model=model,
    output_classes="0;5;6",
    in_class_mode="EDIT_ALL",
    target_classes=[],
    compute_stats="COMPUTE_STATS",
    boundary=None,
    update_pyramid="UPDATE_PYRAMID",
    reference_height=None,
    excluded_class_codes=[],
    batch_size=batch_size
)



class TestInferencing(unittest.TestCase):


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

    
    @parameterized.expand(pixelClassification_params_rgb, skip_on_empty=True)
    def test_pixelClassification(
        self,
        name,
        input_image_path,
        model,
        output_file_path,
        model_args,
        scratch_workspace
    ):
        pixelClassificationInferencing(name, input_image_path, model, output_file_path, model_args, scratch_workspace)


    @parameterized.expand(pixelClassification_params_ms, skip_on_empty=True)
    def test_pixelClassification_ms(
        self,
        name,
        input_image_path,
        model,
        output_file_path,
        model_args,
        scratch_workspace
    ):
        pixelClassificationInferencing(name, input_image_path, model, output_file_path,model_args, scratch_workspace)
            
    
    @parameterized.expand(objectDetection_params_rgb, skip_on_empty=True)
    def test_objectDetection(
        self,
        name,
        input_image_path,
        model,
        output_file_path,
        model_args
    ):
        objectDetectionInferencing(name, input_image_path, model, output_file_path, model_args)


    @parameterized.expand(objectDetection_params_ms, skip_on_empty=True)
    def test_objectDetection_ms(
        self,
        name,
        input_image_path,
        model,
        output_file_path,
        model_args
    ):
        objectDetectionInferencing(name, input_image_path, model, output_file_path, model_args)
    
    def test_text_classification(self):
        arcpy.env.overwriteOutput = True
        in_table = os.path.join(data_inferencing["textclassifier"]["gdb_path"], data_inferencing["textclassifier"]["input_filename"])
        pretrained_model_path_emd = data_inferencing["textclassifier"]["model_path"]
        arcpy.geoai.ClassifyTextUsingDeepLearning(
            in_table,
            "Address",
            pretrained_model_path_emd,
            "ClassLabel",
            "sequence_length 512")

        
    
    def test_entity_recognizer(self):
        in_folder = os.path.join(data_inferencing["entityrecognizer"]["gdb_path"], data_inferencing["entityrecognizer"]["input_filename"])
        arcpy.env.overwriteOutput = True
        pretrained_model_path_emd = data_inferencing["entityrecognizer"]["model_path"]
        out_table = os.path.join(data_inferencing["entityrecognizer"]["gdb_path"], "entity_table")
        arcpy.geoai.ExtractEntitiesUsingDeepLearning(
            in_folder,
            out_table,
            pretrained_model_path_emd,
            "sequence_length 512", 2, "", None)
    
    def test_sequence2sequence(self):
        arcpy.env.overwriteOutput = True
        in_table = os.path.join(data_inferencing["sequence2sequence"]["gdb_path"], data_inferencing["sequence2sequence"]["input_filename"])
        pretrained_model_path_emd = data_inferencing["sequence2sequence"]["model_path"]
        arcpy.geoai.TransformTextUsingDeepLearning(
            in_table,
            "Input",
            pretrained_model_path_emd,
            "Result",
            "sequence_length 512")
    
    @parameterized.expand(detection3d_params, skip_on_empty=True)
    def test_detection3d(
        self,
        name,
        input_path,
        model,
        output_file_path,
        batch_size,
    ):
        detection3dInferencing(name, input_path, model, output_file_path, batch_size)


    @parameterized.expand(classification3d_params, skip_on_empty=True)
    def test_classification3d(
        self,
        name,
        input_path,
        model,
        batch_size,
    ):
        classification3dInferencing(name, input_path, model, batch_size)

    
    @classmethod
    def tearDownClass(cls):
        print("Test cases completed successfully")


if __name__ == "__main__":
    unittest.main()
