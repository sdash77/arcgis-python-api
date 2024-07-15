import types
import unittest
from arcgis.gis import GIS
from arcgis.geoprocessing import GPService, GPTask, GPJob
from utils.decorators import integration_test

SYNC_URL = "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Utilities/PrintingTools/GPServer"
ASYNC_URL = "https://sampleserver5.arcgisonline.com/arcgis/rest/services/911CallsHotspot/GPServer"


@integration_test
class TestGPService(unittest.TestCase):
    """
    Tests the Geoprocessing Service Parent.
    This is the container that holds all the GP Tasks.
    """

    def test_properties(self):
        """tests that the `tasks` returns a collection of GPTask objects"""
        gp = GPService(SYNC_URL, GIS())
        assert gp.properties

    def test_tasks(self):
        """tests that the `tasks` returns a collection of GPTask objects"""
        gp = GPService(SYNC_URL, GIS())
        assert gp.tasks
        if len(gp.tasks) > 0:
            assert isinstance(gp.tasks[0], GPTask)

    def test_refresh(self):
        """tests the service reset"""
        gp = GPService(SYNC_URL, GIS())
        gp.properties
        gp.tasks
        gp.refresh()
        assert gp._properties is None
        assert gp._tasks is None


@integration_test
class TestGPServiceInfo(unittest.TestCase):
    def test_info(self):
        """tests that the `info`"""
        gp = GPService(ASYNC_URL, GIS())
        assert gp.info

    def test_item_info(self):
        """tests that the `item_info`"""
        gp = GPService(ASYNC_URL, GIS())
        assert gp.info.item_info

    def test_info_metadata(self):
        """tests that the `metadata`"""
        gp = GPService(ASYNC_URL, GIS())
        assert gp.info.metadata

    def test_info_thumbnail(self):
        """tests that the `thumbnail`"""
        gp = GPService(ASYNC_URL, GIS())
        assert gp.info.thumbnail


@integration_test
class TestGPTask(unittest.TestCase):
    """
    Tests a single Geoprocessing Service Task.
    Tasks can be run both async and sync depending on the service type.
    """

    def test_async_operation(self):
        gp = GPService(url_or_item=ASYNC_URL, gis=GIS())
        task = gp.tasks[0]
        fn = getattr(task, task.name)
        # Not Default Query
        query = """("DATE" > date '1998-01-01 00:00:00' AND "DATE" < date '1998-01-31 00:00:00') AND ("Day"= 'SAT')"""
        result = fn(query=query)
        assert isinstance(result, GPJob)
        assert result.result()

    def test_task_exists(self):
        gp = GPService(SYNC_URL, GIS())
        task = gp.tasks[0]
        fn = getattr(task, task.name)
        assert isinstance(fn, types.MethodType)

    def test_sync_operation(self):
        gp = GPService(SYNC_URL, GIS())
        task = gp.tasks[1]
        fn = getattr(task, task.name)
        assert fn()

    def test_name(self):
        gp = GPService(SYNC_URL, GIS())
        assert all([isinstance(t.name, str) for t in gp.tasks])

    def test_choice_list(self):
        gp = GPService(SYNC_URL, GIS())
        task = gp.tasks[0]
        cl = task.choice_list
        assert cl

    def test_properties(self):
        gp = GPService(SYNC_URL, GIS())
        task = gp.tasks[0]
        assert isinstance(task, GPTask)
        assert task.properties


if __name__ == "__main__":
    unittest.main()
