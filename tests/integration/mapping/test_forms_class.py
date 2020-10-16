# -------------------------------------------------------------------------------
# Name:        Forms class tests
# Purpose:     Sanity tests for ArcGIS Python API
# -------------------------------------------------------------------------------
import unittest
from integration.dino_utils.dino_precondition_checks import PreconditionChecks
from integration.dino_utils.dino_precondition_checks import PortalUtils
from integration.dino_utils.dino_configs import DinoConfigs
from configparser import ConfigParser
import time

# region PreCondition check
test_skip = False
class_skip = False
module_skip = False

r1 = PreconditionChecks.check_API_import()
r2 = PreconditionChecks.check_Python_version()

if r1 & r2:
    print("## Precondition checks passed ##")
    module_skip = False
else:
    module_skip = True
    print("Pre condition checks failed. Quitting tests")
    raise(exit())

# Import the module after Precondition checks pass
try:
    import arcgis
    from arcgis.gis import GIS
    from arcgis.mapping import WebMap
    from arcgis.mapping.forms import FormCollection, FormInfo, FormGroupElement, FormFieldElement, FormExpressionInfo
except ImportError:
    print("API import error. Quitting test")
    raise(exit())
# endregion PreCondition Check


# TestModule
@unittest.skipIf(module_skip, "Precondition check failed. Skipping tests in GIS module")
def setUpModule():
    """
    Set up code for full arcgis.raster module ImageryLayer class tests
    :return:
    """
    # Get environment status
    print("ArcPy on system: ", PreconditionChecks.check_ArcPy_import())
    print("Is Pro installed: ", PreconditionChecks.check_Pro_installed())
    print("Host OS: " + PreconditionChecks.get_OS())


class Test_Forms(unittest.TestCase):
    """
    Test forms functionality
    """
    @classmethod
    def setUpClass(cls):
        """
        Check if ArcGIS.com can be reached
        :return:
        """

        # region Read config data
        _conf_reader = ConfigParser()
        _conf_reader.read(DinoConfigs.portal_list_file, 'UTF-8')

        cls.portal_url = _conf_reader['workforce_ago']['url']
        cls.portal_username = _conf_reader['workforce_ago']['publisher_user']
        cls.portal_password = _conf_reader['workforce_ago']['publisher_password']
        cls.gis = GIS(cls.portal_url, cls.portal_username, cls.portal_password, verify_cert=False)
        cls.layer_url = "https://sampleserver6.arcgisonline.com/arcgis/rest/services/NapervilleShelters/FeatureServer/0"

        print("==================================================================")
        print("Beginning tests in Test_Forms class")
        # endregion

    def setUp(self):
        self.wm = WebMap()
        fl = arcgis.features.FeatureLayer(url=self.layer_url)
        self.wm.add_layer(fl)
        map_name = "forms " + str(time.time())
        webmap_item_properties = {'title': f'{map_name}',
                                  'snippet': 'Map created using Python API for testing',
                                  'tags': ['automation', 'regression', 'python']}
        self.wm_item = self.wm.save(webmap_item_properties)
        self.forms = self.wm.forms

    def tearDown(self):
        try:
            self.wm_item.delete()
        except Exception:
            pass
        print("------------------------------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_get_form(self):
        try:
            form = self.forms.get_form(title="Shelters")
            self.assertIsInstance(form, FormInfo)
            form = self.forms.get_form(title="blah")
            self.assertEqual(form, None)

        except AssertionError as assertErrorException:
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_get_forms(self):
        try:
            forms = self.forms.get_forms()
            self.assertIsInstance(forms, list)
            self.assertIsInstance(forms[0], FormInfo)

        except AssertionError as assertErrorException:
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_form_info_properties(self):
        try:
            form = self.forms.get_form(title="Shelters")
            form.title = "Shelters Form"
            form.description = "Data collection for shelters"
            self.assertEqual(form.title, "Shelters Form")
            self.assertEqual(form.description, "Data collection for shelters")

        except AssertionError as assertErrorException:
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_form_info_exists(self):
        try:
            form = self.forms.get_form(title="Shelters")
            self.assertEqual(form.exists(), False)
            form.add_element(field_name="facilityid")
            self.assertEqual(form.exists(), True)

        except AssertionError as assertErrorException:
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_form_info_clear_all(self):
        try:
            form = self.forms.get_form(title="Shelters")
            form.add_element(field_name="facilityid")
            self.assertEqual(len(form.elements), 1)
            form.clear_all()
            self.assertEqual(len(form.elements), 0)
            self.assertEqual(form.exists(), False)

        except AssertionError as assertErrorException:
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_form_info_get_element(self):
        try:
            form = self.forms.get_form(title="Shelters")
            el = form.add_element(field_name="facilityid")
            el.label = "Facility ID"
            got_el = form.get_element(label="Facility ID")
            self.assertIsInstance(got_el, FormFieldElement)

            group = FormGroupElement(label="Group 1")
            group = form.add_element(group)
            el = group.add_element(field_name="facname")
            got_el = form.get_element(el.label)
            self.assertIsInstance(got_el, FormFieldElement)

        except AssertionError as assertErrorException:
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_add_element(self):
        try:
            form = self.forms.get_form(title="Shelters")
            form_element = FormFieldElement(label="Facility Name", field_name="facname")
            form.add_element(form_element)
            self.assertEqual(len(form.elements), 1)

            group_element = FormGroupElement(label="Group 1")
            form.add_element(group_element)
            self.assertEqual(len(form.elements), 2)

        except AssertionError as assertErrorException:
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_delete_element(self):
        try:
            form = self.forms.get_form(title="Shelters")
            form_element = FormFieldElement(label="Facility Name", field_name="facname")
            form.add_element(form_element)
            form.add_element(field_name="facilityid")
            self.assertEqual(len(form.elements), 2)

            form.delete_element(form_element)
            form.delete_element(label="facilityid")
            self.assertEqual(len(form.elements), 0)

        except AssertionError as assertErrorException:
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_field_element(self):
        try:
            form = self.forms.get_form(title="Shelters")
            form_element = FormFieldElement(label="Facility Name", field_name="facname", description="test", editable=True, hint="the name",
                                            input_type="text-box")
            form.add_element(form_element)
            self.assertEqual(form.elements[0].label, "Facility Name")
            self.assertEqual(form.elements[0].field_name, "facname")
            self.assertEqual(form.elements[0].description, "test")
            self.assertEqual(form.elements[0].hint, "the name")
            self.assertEqual(form.elements[0].editable, True)
            with self.assertRaises(ValueError):
                form_element.field_name = "blah"

        except AssertionError as assertErrorException:
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_group_element(self):
        try:
            form = self.forms.get_form(title="Shelters")
            group_element = FormGroupElement(label="Group 1", description="test", initial_state="collapsed")
            group = form.add_element(group_element)
            self.assertEqual(group.label, "Group 1")
            self.assertEqual(group.description, "test")
            self.assertEqual(group.initial_state, "collapsed")
            with self.assertRaises(ValueError):
                group.initial_state = "blah"

            el = group.add_element(field_name="facname")
            self.assertEqual(len(group.elements), 1)
            got_el = group.get_element(el.label)
            self.assertIsInstance(got_el, FormFieldElement)
            not_found_el = group.get_element(label="blah")
            self.assertEqual(not_found_el, None)
            group.delete_element(el)
            self.assertEqual(len(group.elements), 0)
            not_deleted_el = group.delete_element(label="blah")
            self.assertEqual(not_deleted_el, False)

        except AssertionError as assertErrorException:
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_form_expression_info(self):
        try:
            form = self.forms.get_form(title="Shelters")
            expression = FormExpressionInfo(title="New Expression", name="expr0", expression="test")
            self.assertEqual(expression.title, "New Expression")
            expression.title = "New Expression 2"
            with self.assertRaises(ValueError):
                expression.name = None
            self.assertEqual(expression.return_type, "boolean")
            expression_2 = FormExpressionInfo(title="New Expression 3", name="expr0", expression="test")
            el = FormFieldElement(label="test", field_name="facname", visibility_expression=expression, required_expression=expression_2)
            form.add_element(el)
            self.assertEqual(len(form.expressions), 2)
            form.delete_element(el)
            self.assertEqual(len(form.expressions), 0)

        except AssertionError as assertErrorException:
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_forms_validation(self):
        try:
            with self.assertRaises(ValueError):
                feature_layer = arcgis.features.FeatureLayer(url="blah")
                FormCollection(parent=feature_layer)
            with self.assertRaises(ValueError):
                self.forms.get_form()
            with self.assertRaises(ValueError):
                FormInfo(layer_data="blah", parent="blah")
            form = self.forms.get_form(title="Shelters")
            self.assertEqual(form.get_element(label="blah"), None)
            self.assertEqual(form.delete_element(label="blah"), False)
            with self.assertRaises(ValueError):
                form._validate_input(element="blah", field="blah")
            with self.assertRaises(ValueError):
                form._validate_input(element="blah")
            with self.assertRaises(ValueError):
                form._validate_input(field=8)
            el = FormFieldElement(field_name="facname")
            with self.assertRaises(ValueError):
                form._validate_element(el)
            with self.assertRaises(ValueError):
                el.element_type = "blah"
            with self.assertRaises(ValueError):
                el.visibility_expression = "blah"

        except AssertionError as assertErrorException:
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())


# TestModule
def tearDownModule():
    print("**End GIS module Tests**")
