import arcpy

data_path = "C:\files_sanoj\inference_testing\raster\5b1b6fb2-5024-4681-a175-9b667174f48c.tif"
output_folder = "C:\files_sanoj\inference_testing\detection_output"
model_path = "C:\files_sanoj\inference_testing\model\palms_houses_e30.dlpk"

with arcpy.EnvManager(extent='-19519319.9244659 -2402912.15167235 -19518974.483775 -2402641.64113133 PROJCS["unnamed_ellipse_Mercator_2SP",GEOGCS["GCS_unnamed_ellipse",DATUM["D_unknown",SPHEROID["Unknown",6378137.0,0.0]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Mercator_2SP"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",0.0],PARAMETER["standard_parallel_1",0.0],UNIT["Meter",1.0]]', scratchWorkspace=r""):
    arcpy.ia.DetectObjectsUsingDeepLearning(
        in_raster=data_path,
        out_detected_objects=r"C:\files_sanoj\Palms and Houses\PalmsAndHouses.gdb\detectedPalms_e1",
        in_model_definition=r"C:\files_sanoj\Palms and Houses\palmtree_training_samples\models\palms_houses_e30\palms_houses_e30.emd",
        arguments="padding 0;threshold 0.5;nms_overlap 0.1;batch_size 64;exclude_pad_detections True;test_time_augmentation False;tta_scales 1",
        run_nms="NMS",
        confidence_score_field="Confidence",
        class_value_field="Class",
        max_overlap_ratio=0.1,
        processing_mode="PROCESS_AS_MOSAICKED_IMAGE",
        use_pixelspace="NO_PIXELSPACE",
        in_objects_of_interest="Palm;House"
    )