
# -------------------------------------------------------------------
# Name:        Common Arcgis Learn Tests.
# Purpose:     Common Tests for arcgis learn to factor same code out.
# -------------------------------------------------------------------
import os
os.environ['ARCGIS_ENABLE_TF_BACKEND'] = '1'
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
try:
    import torch, gc
    from arcgis.learn import prepare_data, EfficientDet
    module_skip = False
    import unittest, traceback
    from integration.arcgis_learn.properties import (
                data_folder
            )
except Exception as e:
    import_exception = "\n".join(
        traceback.format_exception(type(e), e, e.__traceback__)
    )
    module_skip = True

def efficientnet_main():
    data_path = os.path.join(data_folder, "efficientdet_data")
    voc = prepare_data(data_path, dataset_type="PASCAL_VOC_rectangles", batch_size=None)

    detector = EfficientDet(voc, backbone="efficientdet_lite0")

    detector.fit(1)
    detector.save("test_efficientdet")

    loaded_model = detector.from_model(os.path.join(data_path, "models", "test_efficientdet", "test_efficientdet.emd"))
    loaded_model_data = detector.from_model(os.path.join(data_path, "models", "test_efficientdet", "test_efficientdet.dlpk"), voc)

    del detector, loaded_model, loaded_model_data
    gc.collect()
    torch.cuda.empty_cache()


class TestTraining(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Inside Setup Class!!!")

    def setUp(self):
        print("Test: " + self._testMethodName)

    def tearDown(self):
        print("Test:" + self._testMethodName + "is completed.\n")
        print("------------------------------------------------------------------\n")

    @unittest.skipIf(module_skip, "Preconditions not met, skipping test")
    def test_efficientnet(self):
        efficientnet_main()


    @classmethod
    def tearDownClass(cls):
        print("\n All Tests have completed.")
        print("==================================================================")


## Remove all model directories
def tearDownModule():
    print("**End Common Arcgis Learn module Training**")


