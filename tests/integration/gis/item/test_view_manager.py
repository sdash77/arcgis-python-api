import sys
import logging, uuid
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import (
    GIS,
    Item,
    ViewManager,
    ViewLayerDefParameter,
)
from arcgis.gis._impl import SpatialRelationship, SpatialFilter
from utils.decorators import integration_test


__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    root.addHandler(handler)


profiles = ['your_online_profile', 'your_enterprise_profile']
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)

_fs_dict = {
    "objectIdFieldName": "objectid",
    "globalIdFieldName": "globalid",
    "geometryType": "esriGeometryPoint",
    "spatialReference": {"wkid": 102100, "latestWkid": 3857},
    "fields": [
        {
            "name": "objectid",
            "alias": "OBJECTID",
            "type": "esriFieldTypeOID",
        },
        {
            "name": "requestid",
            "alias": "Service Request ID",
            "type": "esriFieldTypeString",
            "length": 25,
        },
        {
            "name": "requesttype",
            "alias": "Problem",
            "type": "esriFieldTypeString",
            "length": 100,
        },
        {
            "name": "comments",
            "alias": "Comments",
            "type": "esriFieldTypeString",
            "length": 255,
        },
        {
            "name": "name",
            "alias": "Name",
            "type": "esriFieldTypeString",
            "length": 150,
        },
        {
            "name": "phone",
            "alias": "Phone Number",
            "type": "esriFieldTypeString",
            "length": 12,
        },
        {
            "name": "email",
            "alias": "Email Address",
            "type": "esriFieldTypeString",
            "length": 100,
        },
        {
            "name": "requestdate",
            "alias": "Date Submitted",
            "type": "esriFieldTypeDate",
            "length": 36,
        },
        {
            "name": "status",
            "alias": "Status",
            "type": "esriFieldTypeString",
            "length": 50,
        },
        {
            "name": "globalid",
            "alias": "GlobalID",
            "type": "esriFieldTypeGlobalID",
            "length": 38,
        },
        {
            "name": "building",
            "alias": "Building Name",
            "type": "esriFieldTypeString",
            "length": 25,
        },
        {
            "name": "floor",
            "alias": "Floor Number",
            "type": "esriFieldTypeString",
            "length": 5,
        },
    ],
    "features": [
        {
            "geometry": {"x": -9809161.170230601, "y": 5123045.5266209831},
            "attributes": {
                "objectid": 246362,
                "requestid": "69",
                "requesttype": "Sidewalk Damage",
                "comments": "Pothole",
                "name": "Foo Bar",
                "phone": "999-9999",
                "email": "foo@foobar.com",
                "requestdate": 1412921609000,
                "status": "Closed",
                "globalid": "{1776024F-0CA5-404E-A133-D442FB6FC0FE}",
                "building": "",
                "floor": "",
            },
        },
        {
            "geometry": {"x": -9074857.9234435894, "y": 4982391.2604217697},
            "attributes": {
                "objectid": 246382,
                "requestid": None,
                "requesttype": "Pothole",
                "comments": "Jhh",
                "name": "Foo Bar",
                "phone": None,
                "email": None,
                "requestdate": None,
                "status": "Unassigned",
                "globalid": "{B424A195-1EC8-4467-AE7E-24BE0EF74383}",
                "building": None,
                "floor": None,
            },
        },
    ],
}


@integration_test
class Test_ItemViewManagerAGOL(unittest.TestCase):
    """Tests the Item View Manager"""

    @classmethod
    def setUpClass(cls):
        cls._gis = GIS(profile='your_online_profile', verify_cert=False)
        from arcgis.features import (
            FeatureSet,
            FeatureLayerCollection,
            FeatureLayer,
        )

        fs = FeatureSet.from_dict(_fs_dict)
        sdf = fs.sdf
        cls._item = cls._gis.content.import_data(sdf)
        cls._item2 = cls._gis.content.import_data(sdf)
        flc = FeatureLayerCollection.fromitem(cls._item)
        cls._view_item = flc.manager.create_view(
            name=f"test_view_{uuid.uuid4().hex[:5]}"
        )

    def test_create_join_view(self):
        """tests the create join view method"""
        from arcgis.gis._impl._dataclasses._viewdc import JoinType

        target = self._item
        fl2 = self._item2.layers[0]
        join_name = f"join_name1235_{uuid.uuid4().hex[:5]}"

        target_join_field = ["status"]
        join = fl2
        join_fields = ["status"]
        join_type = "LEFT"
        include_geometry = True
        vm = target.view_manager
        view_item = vm.create_join_layer(
            join_name=join_name,
            target_join_fields=target_join_field,
            join=join,
            join_fields=join_fields,
            join_type=JoinType.LEFT,
            include_geometry=True,
        )
        assert isinstance(view_item, Item)

    def test_create_view_query_fields(self):
        """ """
        from arcgis.features import (
            FeatureSet,
            FeatureLayerCollection,
            FeatureLayer,
        )

        flc = FeatureLayerCollection.fromitem(self._item)
        mgr = flc.manager
        oid_field = flc.layers[0].properties['objectIdField']
        view_item = mgr.create_view(
            name=f"test_view_{uuid.uuid4().hex[:5]}",
            query=f"{oid_field} > 0",
            visible_fields=["phone", "building", oid_field],
        )
        view_item.delete()

    def test_get_view_manager(self):
        """tests that the logic to get the ViewManger is correct"""
        item = self._item

        assert isinstance(item, Item)
        vm = item.view_manager
        assert vm
        assert isinstance(vm, ViewManager)

    def test_vm_list(self):
        vm = self._item.view_manager
        assert vm.list()
        assert isinstance(vm.list()[0], Item)

    def test_vm_list_defs(self):
        vm = self._item.view_manager
        views = vm.list()
        assert vm.get_definitions(views[0])

    @classmethod
    def tearDownClass(cls):
        assert all([v.delete() for v in cls._item.view_manager.list()])
        item1_data = cls._item.related_items(
            rel_type="Service2Data", direction='forward'
        )
        item2_data = cls._item2.related_items(
            rel_type="Service2Data", direction='forward'
        )
        assert cls._item.delete()
        assert cls._item2.delete()
        [i.delete() for i in item1_data]
        [i.delete() for i in item2_data]
        del cls._gis


class Test_ItemViewManagerEnterprise(unittest.TestCase):
    """Tests the Item View Manager"""

    @classmethod
    def setUpClass(cls):
        cls._gis = GIS(profile='your_enterprise_profile', verify_cert=False)
        from arcgis.features import (
            FeatureSet,
            FeatureLayerCollection,
            FeatureLayer,
        )

        fs = FeatureSet.from_dict(_fs_dict)
        sdf = fs.sdf
        cls._item = cls._gis.content.import_data(sdf)
        flc = FeatureLayerCollection.fromitem(cls._item)
        cls._view_item = flc.manager.create_view(
            name=f"test_view_{uuid.uuid4().hex[:5]}"
        )

    def test_get_view_manager(self):
        """tests that the logic to get the ViewManger is correct"""
        item = self._item

        assert isinstance(item, Item)
        vm = item.view_manager
        assert vm
        assert isinstance(vm, ViewManager)

    def test_vm_list(self):
        vm = self._item.view_manager
        assert vm.list()
        assert isinstance(vm.list()[0], Item)

    def test_vm_list_defs(self):
        vm = self._item.view_manager
        views = vm.list()
        assert vm.get_definitions(views[0])

    @classmethod
    def tearDownClass(cls):
        assert all([v.delete() for v in cls._item.view_manager.list()])
        assert cls._item.delete()
        del cls._gis


if __name__ == "__main__":
    unittest.main()
