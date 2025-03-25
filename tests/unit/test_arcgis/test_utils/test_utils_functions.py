import unittest

from arcgis._impl.common._utils import (
    create_uid,
    inspect_function_inputs,
    _date_handler,
    local_time_to_online,
    bytesto,
    _text_replace,
)


class TestUtilMethods(unittest.TestCase):
    def test_bytesto(self):
        """checks that the bytes to mb works"""
        assert round(bytesto(size=1000000, to="m", bsize=1024)) == 1

    def test_local_time_to_online(self):
        """tests the local to online time"""
        import datetime

        assert local_time_to_online()
        assert local_time_to_online(datetime.datetime.now())

    def test_create_uid(self):
        v = create_uid()
        assert isinstance(v, str)
        assert v

    def test_inspect_function_inputs(self):
        def add(a, b):
            return a + b

        new_params = inspect_function_inputs(add, **{"k": 1, "b": 0, "a": 2})
        assert "a" in new_params
        assert "b" in new_params
        assert add(**new_params) == 2

    def test_text_replace(self):
        text = "hi ho silver, figaro figaro figar0, 123465421235342"
        repl_dict = {"silver": "gold", "figaro": "tra la la", "123": "abc"}
        new_text = _text_replace(text, repl_dict)
        assert new_text == "hi ho gold, tra la la tra la la figar0, abc46542abc5342"


if __name__ == "__main__":
    unittest.main()
