import sys
sys.path.insert(0, r"C:\workspace\geosaurus\tests")
from arcgis.gis import GIS
from arcgis.features import FeatureLayer
from arcgis.map import Map
from arcgis.map.forms import (
    FormInfo,
    FormFieldElement,
    FormBarcodeScannerInput,
    FormComboBoxInput,
    FormDatePickerInput,
    FormDatetimePickerInput,
    FormRadioButtonsInput,
    FormSwitchInput,
    FormTextAreaInput,
    FormTextBoxInput,
    FormTimeInput,
    FormTimestampOffsetPickerInput,
    FormAttachmentElement,
    FormImageInput,
    FormGroupElement,
)
import unittest
from utils.decorators import integration_test, profiles


@profiles.agol
@integration_test
class TestFormInfo(unittest.TestCase):
    """Test the renderers module"""

    def setUp(self):
        self.wm = Map(gis=self.gis)
        assert self.wm

    def test_update_form(self):
        fl = FeatureLayer(
            "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3",
            gis=self.gis,
        )
        assert fl

        self.wm.content.add(fl)
        assert self.wm.content.layers[0]

        field_element = FormFieldElement(
            field_name="TESTING FIELD",
            input_type=FormTextBoxInput(min_length=5, max_length=10),
        )
        field_element2 = FormFieldElement(
            field_name="TESTING FIELD2",
            input_type=FormTextBoxInput(min_length=5, max_length=10),
        )
        form_info = FormInfo(
            description="This is a test form",
            form_elements=[
                field_element,
                field_element2,
            ],
        )
        self.wm.content.update_layer(0, form=form_info)
        form = self.wm.content.form(0)
        assert isinstance(form, FormInfo)

    def test_form_barcodes_scanner_input(self):
        """"""
        barcode_scanner = FormBarcodeScannerInput(
            min_length=5, max_length=10, prefix="TESTING"
        )
        assert barcode_scanner

        form_info = FormInfo(
            description="This is a test form",
            form_elements=[
                FormFieldElement(
                    field_name="TESTING FIELD",
                    input_type=barcode_scanner,
                ),
            ],
        )
        assert form_info

    def test_form_combo_box_input(self):
        """"""
        combo_box = FormComboBoxInput(no_value_option_label="test", prefix="TESTING")
        assert combo_box

        form_info = FormInfo(
            description="This is a test form",
            form_elements=[
                FormFieldElement(
                    field_name="TESTING FIELD",
                    input_type=combo_box,
                ),
            ],
        )
        assert form_info

    def test_form_date_picker_input(self):
        """"""
        date_picker = FormDatePickerInput(min="2020-01-01", max="2020-12-31")
        assert date_picker

        form_info = FormInfo(
            description="This is a test form",
            form_elements=[
                FormFieldElement(
                    field_name="TESTING FIELD",
                    input_type=date_picker,
                ),
            ],
        )
        assert form_info

    def test_form_date_time_picker_input(self):
        """"""
        import datetime

        mindatetime = datetime.datetime(2020, 1, 1, 0, 0)
        maxdatetime = datetime.datetime(2020, 12, 31, 23, 59)
        date_time_picker = FormDatetimePickerInput(
            min=int(mindatetime.timestamp()),
            max=int(maxdatetime.timestamp()),
            include_time=True,
        )
        assert date_time_picker

        form_info = FormInfo(
            description="This is a test form",
            form_elements=[
                FormFieldElement(
                    field_name="TESTING FIELD",
                    input_type=date_time_picker,
                ),
            ],
        )
        assert form_info

    def test_form_radio_button_input(self):
        """"""
        radio_button = FormRadioButtonsInput(no_value_option_label="test")
        assert radio_button

        form_info = FormInfo(
            description="This is a test form",
            form_elements=[
                FormFieldElement(
                    field_name="TESTING FIELD",
                    input_type=radio_button,
                ),
            ],
        )
        assert form_info

    def test_form_switch_input(self):
        """"""
        switch = FormSwitchInput(off_value="0", on_value="1")
        assert switch

        form_info = FormInfo(
            description="This is a test form",
            form_elements=[
                FormFieldElement(
                    field_name="TESTING FIELD",
                    input_type=switch,
                ),
            ],
        )
        assert form_info

    def test_form_text_area_input(self):
        """"""
        text_area = FormTextAreaInput(min_length=5, max_length=10)
        assert text_area

        form_info = FormInfo(
            description="This is a test form",
            form_elements=[
                FormFieldElement(
                    field_name="TESTING FIELD",
                    input_type=text_area,
                ),
            ],
        )
        assert form_info

    def test_form_test_box_input(self):
        """"""
        text_box = FormTextBoxInput(min_length=5, max_length=10)
        assert text_box

        form_info = FormInfo(
            description="This is a test form",
            form_elements=[
                FormFieldElement(
                    field_name="TESTING FIELD",
                    input_type=text_box,
                ),
            ],
        )
        assert form_info

    def test_form_time_input(self):
        """"""
        time_input = FormTimeInput(min="00:00", max="23:59", timeResolution="minutes")
        assert time_input

        form_info = FormInfo(
            description="This is a test form",
            form_elements=[
                FormFieldElement(
                    field_name="TESTING FIELD",
                    input_type=time_input,
                ),
            ],
        )
        assert form_info

    def test_form_timestamp_offset_picker_input(self):
        """"""
        timestamp_offset_picker = FormTimestampOffsetPickerInput(
            min="2020-01-01", max="2020-12-31", include_time=True
        )
        assert timestamp_offset_picker

        form_info = FormInfo(
            description="This is a test form",
            form_elements=[
                FormFieldElement(
                    field_name="TESTING FIELD",
                    input_type=timestamp_offset_picker,
                ),
            ],
        )
        assert form_info

    def test_form_attachment_element(self):
        """"""
        attachment_element = FormAttachmentElement(
            attachment_keyword="Testing Attachment",
            description="Testing",
            input_type=FormImageInput(),
            label="Test"
        )
        assert attachment_element

        form_info = FormInfo(
            description="This is a test form",
            form_elements=[
                attachment_element,
            ],
        )
        assert form_info

    def test_form_group_element(self):
        """"""
        group_element = FormGroupElement(
            description="Testing",
            form_elements=[
                FormFieldElement(
                    field_name="TESTING FIELD",
                    input_type=FormTextBoxInput(min_length=5, max_length=10),
                ),
                FormFieldElement(
                    field_name="TESTING FIELD2",
                    input_type=FormTextBoxInput(min_length=5, max_length=10),
                ),
            ],
        )
        assert group_element

        form_info = FormInfo(
            description="This is a test form",
            form_elements=[
                group_element,
            ],
        )
        assert form_info


if __name__ == "__main__":
    unittest.main()
