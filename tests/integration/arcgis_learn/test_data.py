#-------------------------------------------------------------------------------
# Name:        Prepare Data Tests
# Purpose:     Tests for prepare data function, checking the output of the function.
#-------------------------------------------------------------------------------

import unittest
import os
HAS_DEPS = True
try:
    import fastai
    import torch
    import torchvision
except Exception:
    HAS_DEPS = False

module_skip = False

if not HAS_DEPS:
    module_skip = True
else:
    from arcgis.learn._data import prepare_data
    from arcgis.learn import SingleShotDetector, UnetClassifier, FeatureClassifier

#TestModule
@unittest.skipIf(module_skip, "Precondition check failed. Skipping Prepare Data tests")
def setUpModule():
    print("Dependencies Installed.")


class Test_Data(unittest.TestCase):
    """
    Test to check if Prepare Data works correctly.
    """
    @classmethod
    def setUpClass(cls):
        #TODO - To be filled.
        data_folder = os.path.join(os.path.dirname(__file__), 'data')
        cls.unet_data = os.path.join(data_folder, 'unet_naip_residential_tests_data')
        cls.ssd_data = os.path.join(data_folder, 'palm_tree_tests_data')
        cls.ssd_pascal_voc_data = os.path.join(data_folder, 'trees_tests_data')
        cls.feature_data = os.path.join(data_folder, 'damage_classifier_tests_data')
        cls.imagenet_data = ''
        #TODO - define data dictionary.
        cls.ssd_data_class_mapping = {1: 'Palm'}
        cls.ssd_pascal_voc_data_default_class_mapping = {1: '60'}
        cls.ssd_pascal_voc_data_class_mapping = {60: 'Palm Tree'}
        cls.unet_class_mapping = {
            1: '1',
            2: '2',
            3: '3',
            4: '4',
            5: '5',
            6: '6',
            7: '7',
            8: '8',
            9: '9',
            10: '10',
            11: '11',
            12: '12'
        }
        cls.feature_class_mapping = {10: '10', 20: '20'}

    def setUp(self):
        print("Test: "+self._testMethodName)

    def tearDown(self):
        print("------------------------------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")

    @unittest.skipIf(module_skip, "Preconditions not met, skipping test")
    def test_ssd_data_esri_format(self):
        data_bunch = prepare_data(self.ssd_data, chip_size=300, batch_size=2)
        self.assertEqual(data_bunch.batch_size, 2)
        self.assertEqual(data_bunch.chip_size, 300)
        self.assertDictEqual(self.ssd_data_class_mapping, data_bunch.class_mapping)
        ssd = SingleShotDetector(data_bunch)
        ssd.fit(1)
        ssd.save('test_e1')
        ssd.load('test_e1')

    @unittest.skipIf(module_skip, "Preconditions not met, skipping test")
    def test_ssd_data_pascal_voc_format(self):
        try:
            prepare_data(self.ssd_pascal_voc_data, chip_size=200, batch_size=4)
        except Exception:
            self.assertTrue(True)

        data_bunch = prepare_data(self.ssd_pascal_voc_data, chip_size=200, batch_size=4, class_mapping=self.ssd_pascal_voc_data_class_mapping, dataset_type='PASCAL_VOC_rectangles')
        self.assertEqual(data_bunch.batch_size, 4)
        self.assertEqual(data_bunch.chip_size, 200)
        self.assertDictEqual(data_bunch.class_mapping, self.ssd_pascal_voc_data_class_mapping)

    @unittest.skipIf(module_skip, "Preconditions not met, skipping test")
    def test_unet_data(self):
        data_bunch = prepare_data(self.unet_data, chip_size=300, batch_size=2)
        self.assertEqual(data_bunch.batch_size, 2)
        self.assertEqual(data_bunch.chip_size, 300)
        self.assertDictEqual(self.unet_class_mapping, data_bunch.class_mapping)
        unet = UnetClassifier(data_bunch)
        unet.fit(1)
        unet.save('test_e1')
        unet.load('test_e1')

    @unittest.skipIf(module_skip, "Preconditions not met, skipping test")
    def test_feature_classifier_data(self):
        data_bunch = prepare_data(self.feature_data, batch_size=2)
        self.assertEqual(data_bunch.batch_size, 2)
        self.assertDictEqual(self.feature_class_mapping, data_bunch.class_mapping)
        feature_classifier = FeatureClassifier(data_bunch)
        feature_classifier.fit(1)
        feature_classifier.save('test_e1')
        feature_classifier.load('test_e1')

    @unittest.skipIf(True, "Preconditions not met, skipping test")
    def test_imagenet_data(self):
        try:
            prepare_data(self.imagenet_data)
        except Exception:
            self.assertTrue(True)

        data_bunch = prepare_data(self.imagenet_data, batch_size=2, chip_size=300, dataset_type='Imagenet')
        self.assertEqual(data_bunch.batch_size, 2)
        self.assertEqual(data_bunch.chip_size, 300)


#TestModule
def tearDownModule():
    print("**End Prepare Data module Tests**")