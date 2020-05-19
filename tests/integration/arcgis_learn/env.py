import os

def setupenviron():
    #Add all environment variables.
    
    # Object Detection Data.
    os.environ["object_detection_data1"] = r'/mnt/Raster/Data/Tests_Data/object_detection/data1'
    os.environ["object_detection_data2"] = r'/mnt/Raster/Data/Tests_Data/object_detection/data2'
    os.environ["object_detection_data3"] = r"/mnt/Raster/Data/Tests_Data/object_detection/data3"

    os.environ["object_detection_inferencing_data1"] = r"/mnt/Raster/Data/Tests_Data/inferencing data/palm tree data/Test_Data.tif"
    os.environ["object_detection_inferencing_data2"] = "Test Data 2"

    os.environ['object_detection_sample_images_1'] = '000000011.tif;000000079.tif;000000073.tif;000000014.tif;000000055.tif'
    os.environ['object_detection_sample_images_2'] = '000000014.png;000000093.png;000000056.png;000000087.png;000000044.png'

    # SSD Data.
    os.environ["model_ssd_162"] = r'/mnt/Raster/Data/Tests_Data/models/ssd/162/162.emd'
    os.environ["model_ssd_170"] = r'/mnt/Raster/Data/Tests_Data/models/ssd/170/170.emd'

    os.environ["object_detection_inferencing_result_ssd"] = r"/mnt/Raster/Data/Tests_Data/inferencing output/object_detection/palm tree ssd.shp"
    os.environ["object_detection_inferencing_ssd_args"] = "padding 56;nms_overlap 0.2;threshold 0.5;batch_size 4;exclude_pad_detections True"

    # Retinanet Data.
    os.environ["model_rn_170"] = r"/mnt/Raster/Data/Tests_Data/models/retinanet/170/ret_model/israel_test_rnet.emd"

    os.environ["object_detection_inferencing_result_rn"] = r"/mnt/Raster/Data/Tests_Data/inferencing output/object_detection/palm tree rn.shp"
    os.environ["object_detection_inferencing_rn_args"] = "padding 56;nms_overlap 0.2;threshold 0.5;batch_size 4;exclude_pad_detections True"

    os.environ["object_detection_inferencing_result_maskrcnn"] = r"/mnt/Raster/Data/Tests_Data/inferencing output/object_detection/palm tree maskrcnn.shp"
    os.environ["object_detection_inferencing_maskrcnn_args"] = "padding 56;threshold 0.5;batch_size 4;return_bboxes False"

    os.environ["pixel_classification_data1"] = r"/mnt/Raster/Data/Tests_Data/pixel_classification/data1"
    os.environ["pixel_classification_inferencing_data1"] = r"/mnt/Raster/Data/Tests_Data/inferencing data/palm tree data/Test_Data.tif"

    # PSPNet Data.
    os.environ["model_pspnet_170"] = r"/mnt/Raster/Data/Tests_Data/models/pspnet/170/psnet_model/psnet_model.emd"

    # MaskRCNN Data.
    os.environ["maskrcnn_data1"] = r"/mnt/Raster/Data/Tests_Data/maskrcnn/data1"

    os.environ["model_maskrcnn_170"] = r"/mnt/Raster/Data/Tests_Data/models/maskrcnn/maskrcnn-model/maskrcnn-model.emd"

    # Feature Classification.
    os.environ["feature_classification_data1"] = r"/mnt/Raster/Data/Tests_Data/feature_classification/data1"

    from datetime import datetime
    os.environ['feature_classification_inferencing_data1'] = r"/mnt/Raster/Data/Tests_Data/inferencing data/parking lot data/parkinglot.shp"
    os.environ["feature_classification_inferencing_in_raster"] = r"/mnt/Raster/Data/Tests_Data/inferencing data/world_imagery.tif"
    os.environ["inferencing_result_fc"] = r"C:/Users/anga8862/Documents/ArcGIS/Projects/MyProject/MyProject.gdb/result_{0}".format(datetime.now().strftime("%Y%m%d%H%M%S"))

    os.environ["model_fc_162"] = r"/mnt/Raster/Data/Tests_Data/models/fc/162/damage_classifier/damage_classifier.emd"
    os.environ["model_fc_170"] = r"/mnt/Raster/Data/Tests_Data/models/fc/170/arcgis_pro_test_res50/arcgis_pro_test_res50.emd"


    # Unet Classifier.
    os.environ["model_unet_162"] = r"/mnt/Raster/Data/Tests_Data/models/unet/162/unet_model/unet_model.emd"
    os.environ["model_unet_170"] = r"/mnt/Raster/Data/Tests_Data/models/unet/170/unet_model/unet_model.emd"

    os.environ['run_backbones'] = '0'
    os.environ['run_inferencing'] = '0'

    # Notebook Tests
    os.environ["notebook_test"] = r"/mnt/Raster/Data/testdata/extracted_data/object_detection_data/palm-tree-256/test-object-det"