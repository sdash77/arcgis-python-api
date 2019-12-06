# -------------------------------------------------------------------------------
# Name:        SingleShotDetector Tests
# Purpose:     Tests for SingleShotDetector.
# -------------------------------------------------------------------------------

import unittest
import os

os.environ["CUDA_VISIBLE_DEVICES"] = '0'

HAS_DEPS = True
try:
    import fastai
    import torch
    import torchvision
    from torchvision import models
except Exception:
    HAS_DEPS = False

module_skip = False

if not HAS_DEPS:
    module_skip = True
else:
    from arcgis.learn import SingleShotDetector, prepare_data

# TestModule
@unittest.skipIf(module_skip, "Precondition check failed. Skipping Prepare Data tests")
def setUpModule():
    os.system(f'rmdir /s /q "{os.path.join(os.environ["object_detection_data1"], "models")}"')
    os.system(f'rmdir /s /q "{os.path.join(os.environ["object_detection_data1"], "images/models")}"')

    os.system(f'rmdir /s /q "{os.path.join(os.environ["object_detection_data2"], "models")}"')
    os.system(f'rmdir /s /q "{os.path.join(os.environ["object_detection_data2"], "images/models")}"')

    os.system(f'rmdir /s /q "{os.path.join(os.environ["object_detection_data3"], "models")}"')
    os.system(f'rmdir /s /q "{os.path.join(os.environ["object_detection_data3"], "images/models")}"')

    print("Dependencies Installed.")


class Test_SSD(unittest.TestCase):
    """
    Test to check if Single Shot Detector works correctly.
    """

    @classmethod
    def setUpClass(cls):
        cls.data1 = os.environ["object_detection_data1"]
        cls.data2 = os.environ["object_detection_data2"]

        #Semicolin separated list of images.
        cls.sample_images_1 = os.environ['object_detection_sample_images_1'].split(';')
        cls.sample_images_2 = os.environ['object_detection_sample_images_2'].split(';')

        cls.ssd_data_class_mapping = {1: 'Palm', 2: 'House'}

    def setUp(self):
        print("Test: " + self._testMethodName)

    def tearDown(self):
        print("------------------------------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")

    @unittest.skipIf(module_skip, "Preconditions not met, skipping test")
    def test_1_initial_model(self):
        data_bunch = prepare_data(self.data2, chip_size=300, batch_size=2)
        self.assertDictEqual(self.ssd_data_class_mapping, data_bunch.class_mapping)
        ssd = SingleShotDetector(data_bunch)

        ssd.average_precision_score()
        ssd.fit(1, lr=0.001)
        ssd.average_precision_score()
        ssd.save('post_fit_ssd')

        self.assertEqual(ssd._emd_template["Framework"], "arcgis.learn.models._inferencing")
        self.assertEqual(ssd._emd_template["InferenceFunction"], "ArcGISObjectDetector.py")
        self.assertEqual(ssd._emd_template["ModelConfiguration"], "_DynamicSSD")
        self.assertEqual(ssd._emd_template["ImageHeight"], 300)
        self.assertEqual(ssd._emd_template["ImageWidth"], 300)
        self.assertEqual(ssd._emd_template["ModelType"], "ObjectDetection")
        self.assertEqual(ssd._emd_template["ModelParameters"]["backbone"], "resnet34")
        self.assertEqual(ssd._emd_template["SSDVersion"], 2)

    @unittest.skipIf(module_skip, "Preconditions not met, skipping test")
    def test_2_load_from_model(self):
        # Without Databunch.
        data_bunch = prepare_data(self.data2, chip_size=300, batch_size=2)
        ssd = SingleShotDetector.from_model(os.path.join(self.data2, 'models/post_fit_ssd/post_fit_ssd.emd'))
        for sample_image in self.sample_images_2:
            path = os.path.join(self.data2, f'images/{sample_image}')
            values = ssd.predict(path)
            self.assertEqual(len(values), 2)
            values = ssd.predict(path, return_scores=True)
            self.assertEqual(len(values), 3)

        # With Databunch.
        ssd = SingleShotDetector.from_model(os.path.join(self.data2, 'models/post_fit_ssd/post_fit_ssd.emd'), data_bunch)
        for sample_image in self.sample_images_2:
            path = os.path.join(self.data2, f'images/{sample_image}')
            values = ssd.predict(path)
            self.assertEqual(len(values), 2)
            values = ssd.predict(path, return_scores=True)
            self.assertEqual(len(values), 3)

    # Model Accuracy Test, minimum 40%
    @unittest.skipIf(module_skip, "Preconditions not met, skipping test")
    def test_4_model_accuracy(self):
        input_data = os.environ["object_detection_data3"]
        data = prepare_data(input_data)
        ssd = SingleShotDetector(data)
        ssd.fit(10)
        self.assertGreater(ssd.average_precision_score(mean=True), .40)


# TestModule
def tearDownModule():
    os.system(f'rmdir /s /q "{os.path.join(os.environ["object_detection_data1"], "models")}"')
    os.system(f'rmdir /s /q "{os.path.join(os.environ["object_detection_data1"], "images/models")}"')

    os.system(f'rmdir /s /q "{os.path.join(os.environ["object_detection_data2"], "models")}"')
    os.system(f'rmdir /s /q "{os.path.join(os.environ["object_detection_data2"], "images/models")}"')

    os.system(f'rmdir /s /q "{os.path.join(os.environ["object_detection_data3"], "models")}"')
    os.system(f'rmdir /s /q "{os.path.join(os.environ["object_detection_data3"], "images/models")}"')

    print("**End SSD module Tests**")



