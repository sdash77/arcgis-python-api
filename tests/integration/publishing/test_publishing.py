import sys
import logging
import unittest
from integration.config import QALAB_ROOT_PATH
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from utils.decorators import integration_test

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    root.addHandler(handler)


SOURCE_DATA_LOCATION = (
   QALAB_ROOT_PATH + "\publishing_test_data"
)
profiles = ['your_online_profile', 'your_enterprise_profile']
PROXIES = detect_proxy(True)  # Handles Fiddler when True
proxies = PROXIES
enable_verbose_logging(__logger__)

import os
from arcgis.gis import GIS, ItemProperties, ItemTypeEnum
from arcgis.gis import ContentManager
from arcgis.gis._impl._content_manager import _publish as publish
from arcgis.gis._impl._content_manager import (
    PublishFileTypes,
    PublishOutputTypes,
    PublishJob,
)

import uuid


def clean_up_items(gis):
    files = [
        "CanadaCensusMapTest.vtpk",
        "japan_dl_tpkx.tpkx",
        "lyon_trees2.slpk",
    ]
    for f in files:
        if gis.content.search(f):
            [i.delete() for i in gis.content.search(f)]



@integration_test
class TestPublishingTPKAGOL(unittest.TestCase):
    """Tests the publishing the vector tile package process"""

    @classmethod
    def setUpClass(cls):
        cls.gis = GIS(
            profile='your_online_profile',
            verify_cert=False,
            trust_env=True,
            proxy=proxies,
        )
        cls.source_path = SOURCE_DATA_LOCATION
        cls.data = {}
        cls.pitems = []
        gis: GIS = cls.gis
        clean_up_items(gis=gis)
        cm: ContentManager = gis.content
        folder = cm.folders.get()
        
        ### Vector Tile Package
        ip = ItemProperties(
            title=f"data_{uuid.uuid4().hex[:3]}",
            item_type=ItemTypeEnum.VECTOR_TILE_PACKAGE,
        )
        vtpk_item = folder.add(
            item_properties=ip,
            file=os.path.join(
                cls.source_path, "packages", "CanadaCensusMapTest.vtpk"
                ),
        ).result()
        cls.data['vtpk'] = vtpk_item
        
        ## Tile Package
        ip = ItemProperties(
            title=f"data_{uuid.uuid4().hex[:3]}",
            item_type=ItemTypeEnum.TILE_PACKAGE,
        )
        tpk_item = folder.add(
            item_properties=ip,
            file=os.path.join(
                cls.source_path, "packages", "japan_dl_tpkx.tpkx"
            ),
        ).result()
        cls.data['tpkg'] = tpk_item
        ## Scene Package
        ip = ItemProperties(
            title=f"data_{uuid.uuid4().hex[:3]}",
            item_type=ItemTypeEnum.SCENE_PACKAGE,
        )
        slpk_item = folder.add(
            item_properties=ip,
            file=os.path.join(
                cls.source_path, "packages", "lyon_trees2.slpk"
            ),
        ).result()
        cls.data['scene'] = slpk_item

    # @unittest.skip("i work")
    def test_publish_vtpk_no_params(self):
        if "vtpk" in self.data:
            item = publish(item=self.data['vtpk'])
            self.pitems.append(item.result())

    # @unittest.skip("i work")
    def test_publish_vtpk_params(self):
        if "vtpk" in self.data:
            item = publish(
                item=self.data['vtpk'],
                publish_parameters={
                    #"name": self.data['tpkg'].title.replace(" ", "_"),
                    "name": self.data['tpkg'].title + "_apiTest",
                    "maxRecordCount": 2000,
                },
            )
            self.pitems.append(item.result())

    # @unittest.skip("i work")
    def test_tile_package_no_params(self):
        if "tpkg" in self.data:
            with self.assertRaises(Exception):
                item = publish(item=self.data['tpkg'])
                self.pitems.append(item.result())

    # @unittest.skip("i work")
    def test_tile_package_params(self):
        if "tpkg" in self.data:
            task = publish(
                item=self.data['tpkg'],
                publish_parameters={
                    #"name": self.data['tpkg'].title.replace(" ", "_"),
                    "name": self.data['tpkg'].title + "_apiTest",
                    "maxRecordCount": 2000,
                },
            )
            publish_item = task.result()
            cache_task = task.build_cache()
            assert cache_task
            assert cache_task.result()
            self.pitems.append(publish_item)

    # @unittest.skip("i work")
    def test_scene_package_no_params(self):
        if "scene" in self.data:
            with self.assertRaises(Exception):
                item = publish(item=self.data['scene'])
                self.pitems.append(item.result())

    # @unittest.skip("i work")
    def test_scene_package_params(self):
        if "scene" in self.data:
            item = publish(
                item=self.data['scene'],
                publish_parameters={
                    #"name": self.data['scene'].title.replace(" ", "_"),
                    "name": self.data['scene'].title + "_apiTest",
                    "maxRecordCount": 2000,
                },
            )
            self.pitems.append(item.result())

    @classmethod
    def tearDownClass(cls):
        for i in cls.pitems:
            try:
                i.delete(permanent=True)
            except:
                print(i)
        for k, v in cls.data.items():
            try:
                v.delete(permanent=True)
            except:
                print(f"{k} in {v}")


# @unittest.skip("i work")
@integration_test
class TestPublishingTPKEnterprise(unittest.TestCase):
    """Tests the publishing the vector tile package process"""

    @classmethod
    def setUpClass(cls):
        cls.gis = GIS(
            profile='your_enterprise_profile',
            verify_cert=False,
            trust_env=True,
            proxy=proxies,
        )
        cls.source_path = SOURCE_DATA_LOCATION
        cls.data = {}
        cls.pitems = []
        gis: GIS = cls.gis
        clean_up_items(gis=gis)
        cm: ContentManager = gis.content
        folder = cm.folders.get()
        # Vector Tile Package
        ip = ItemProperties(
            title=f"data_{uuid.uuid4().hex[:3]}",
            item_type=ItemTypeEnum.VECTOR_TILE_PACKAGE,
        )
        vtpk_item = folder.add(
            item_properties=ip,
            file=os.path.join(
                cls.source_path, "packages", "CanadaCensusMapTest.vtpk"
            ),
        ).result()
        cls.data['vtpk'] = vtpk_item
        # Tile Package
        ip = ItemProperties(
            title=f"data_{uuid.uuid4().hex[:3]}",
            item_type=ItemTypeEnum.TILE_PACKAGE,
        )
        tpk_item = folder.add(
            item_properties=ip,
            file=os.path.join(
                cls.source_path, "packages", "japan_dl_tpkx.tpkx"
            ),
        ).result()
        cls.data['tpkg'] = tpk_item
        # Scene Package
        ip = ItemProperties(
            title=f"data_{uuid.uuid4().hex[:3]}",
            item_type=ItemTypeEnum.SCENE_PACKAGE,
        )
        slpk_item = folder.add(
            item_properties=ip,
            file=os.path.join(
                cls.source_path, "packages", "lyon_trees2.slpk"
            ),
        ).result()
        cls.data['scene'] = slpk_item

    # @unittest.skip("i work")
    def test_publish_vtpk_no_params(self):
        if "vtpk" in self.data:
            item = publish(item=self.data['vtpk'])
            self.pitems.append(item.result())

    # @unittest.skip("i work")
    def test_publish_vtpk_params(self):
        if "vtpk" in self.data:
            item = publish(
                item=self.data['vtpk'],
                publish_parameters={
                    #"name": self.data['tpkg'].title.replace("", "_"),
                    "name": self.data['tpkg'].title + "_apiTest",
                    "maxRecordCount": 2000,
                },
            )
            self.pitems.append(item.result())

    # @unittest.skip("i work")
    # publish parameters are required for tilePackage
    def test_tile_package_no_params(self):
        if "tpkg" in self.data:
            with self.assertRaises(Exception):
                item = publish(item=self.data['tpkg'])
                self.pitems.append(item.result())

    # @unittest.skip("i work")
    def test_tile_package_params(self):
        if "tpkg" in self.data:
            item = publish(
                item=self.data['tpkg'],
                publish_parameters={
                    #"name": self.data['tpkg'].title.replace(" ", "_"),
                    "name": self.data['tpkg'].title + "_apiTest",
                    "maxRecordCount": 2000,
                },
            )
            self.pitems.append(item.result())

    # @unittest.skip("i work")
    # publish parameters are required for scene layer packages
    def test_scene_package_no_params(self):
        if "scene" in self.data:
            with self.assertRaises(Exception):
                item = publish(item=self.data['scene'])
                self.pitems.append(item.result())

    # @unittest.skip("i work")
    def test_scene_package_params(self):
        if "scene" in self.data:
            item = publish(
                item=self.data['scene'],
                publish_parameters={
                    #"name": self.data['scene'].title.replace(" ", "_"),
                    "name": self.data['scene'].title + "_apiTest",
                    "maxRecordCount": 2000,
                },
            )
            self.pitems.append(item.result())

    @classmethod
    def tearDownClass(cls):
        for i in cls.pitems:
            try:
                i.delete()
            except:
                print(i)
        for k, v in cls.data.items():
            try:
                v.delete()
            except:
                print(f"{k} in {v}")


# @unittest.skip("i work")
@integration_test
class TestPublishingNoParmetersEnterprise(unittest.TestCase):
    """Tests the publishing process for with datasets that do not have publish parameters"""

    @classmethod
    def setUpClass(cls):
        cls.gis = GIS(
            profile='your_enterprise_profile',
            verify_cert=False,
            trust_env=True,
            proxy=proxies,
        )
        cls.source_path = SOURCE_DATA_LOCATION
        cls.data = {}
        cls.pitems = []
        gis: GIS = cls.gis
        clean_up_items(gis=gis)
        cm: ContentManager = gis.content
        folder = cm.folders.get()
        # Shapefile
        ip = ItemProperties(
            title=f"data_{uuid.uuid4().hex[:3]}",
            item_type=ItemTypeEnum.SHAPEFILE,
        )
        shape_item = folder.add(
            item_properties=ip,
            file=os.path.join(cls.source_path, "shapefile_cities.zip"),
        ).result()
        cls.data['shapefile'] = shape_item
        # File Geodatabase
        ip = ItemProperties(
            title=f"data_{uuid.uuid4().hex[:3]}",
            item_type=ItemTypeEnum.FILE_GEODATABASE,
        )
        fgdb_item = folder.add(
            item_properties=ip,
            file=os.path.join(cls.source_path, "fgdb_companies.zip"),
        ).result()
        cls.data['fgdb'] = fgdb_item
        #  GEOPACKAGE
        ip = ItemProperties(
            title=f"data_{uuid.uuid4().hex[:3]}",
            item_type=ItemTypeEnum.GEOPACKAGE,
        )
        gpkg_item = folder.add(
            item_properties=ip,
            file=os.path.join(cls.source_path, "GPKG_data.gpkg"),
        ).result()
        cls.data['gpkg'] = gpkg_item
        #  CSV
        ip = ItemProperties(
            title=f"data_{uuid.uuid4().hex[:3]}",
            item_type=ItemTypeEnum.CSV,
        )
        csv_item = folder.add(
            item_properties=ip,
            file=os.path.join(cls.source_path, "csv_dataset.csv"),
        ).result()
        cls.data['csv'] = csv_item

        #  Excel
        ip = ItemProperties(
            title=f"data_{uuid.uuid4().hex[:3]}",
            item_type=ItemTypeEnum.MICROSOFT_EXCEL,
        )
        excel_item = folder.add(
            item_properties=ip,
            file=os.path.join(cls.source_path, "excel_dataset.xlsx"),
        ).result()
        cls.data['excel'] = excel_item

        # Service Definition
        ip = ItemProperties(
            title=f"data_{uuid.uuid4().hex[:3]}",
            item_type=ItemTypeEnum.SERVICE_DEFINITION,
        )
        sd_item = folder.add(
            item_properties=ip,
            file=os.path.join(
                cls.source_path,
                "NJ_Roadway_Network_Enterprise_11x.sd",
            ),
        ).result()
        cls.data['sd'] = sd_item

    # @unittest.skip("i work")
    def test_publish_fgdb(self):
        if "fgdb" in self.data:
            self.pitems.append(publish(item=self.data['fgdb']).result())

    # @unittest.skip("i work")
    def test_publish_sd(self):
        if "sd" in self.data:
            item = self.data['sd']
            self.pitems.append(publish(item=item).result())

    # @unittest.skip("i work")
    def test_publish_geopackage(self):
        if "gpkg" in self.data:
            self.pitems.append(publish(item=self.data['gpkg']).result())

    # @unittest.skip("i work")
    def test_publish_shapefile(self):
        if "shapefile" in self.data:
            self.pitems.append(publish(item=self.data['shapefile']).result()) 

    @classmethod
    def tearDownClass(cls):
        for i in cls.pitems:
            try:
                i.delete()
            except:
                print(i)
        for k, v in cls.data.items():
            try:
                v.delete()
            except:
                print(f"{k} in {v}")


# @unittest.skip("i work")
@integration_test
class TestPublishingNoParmetersAGOL(unittest.TestCase):
    """Tests the publishing process for with datasets that do not have publish parameters"""

    @classmethod
    def setUpClass(cls):
        cls.gis = GIS(
            profile='your_dev_online_profile',
            verify_cert=False,
            trust_env=True,
            proxy=proxies,
        )
        cls.source_path = SOURCE_DATA_LOCATION
        cls.data = {}
        cls.pitems = []
        gis: GIS = cls.gis
        clean_up_items(gis=gis)
        cm: ContentManager = gis.content
        folder = cm.folders.get()
        # Shapefile
        ip = ItemProperties(
            title=f"data_{uuid.uuid4().hex[:3]}",
            item_type=ItemTypeEnum.SHAPEFILE,
        )
        shape_item = folder.add(
            item_properties=ip,
            file=os.path.join(cls.source_path, "shapefile_cities.zip"),
        ).result()
        cls.data['shapefile'] = shape_item
        # File Geodatabase
        ip = ItemProperties(
            title=f"data_{uuid.uuid4().hex[:3]}",
            item_type=ItemTypeEnum.FILE_GEODATABASE,
        )
        fgdb_item = folder.add(
            item_properties=ip,
            file=os.path.join(cls.source_path, "fgdb_companies.zip"),
        ).result()
        cls.data['fgdb'] = fgdb_item
        #  GEOPACKAGE
        ip = ItemProperties(
            title=f"data_{uuid.uuid4().hex[:3]}",
            item_type=ItemTypeEnum.GEOPACKAGE,
        )
        gpkg_item = folder.add(
            item_properties=ip,
            file=os.path.join(cls.source_path, "GPKG_data.gpkg"),
        ).result()
        cls.data['gpkg'] = gpkg_item
        #  CSV
        ip = ItemProperties(
            title=f"data_{uuid.uuid4().hex[:3]}",
            item_type=ItemTypeEnum.CSV,
        )
        csv_item = folder.add(
            item_properties=ip,
            file=os.path.join(cls.source_path, "csv_dataset.csv"),
        ).result()
        cls.data['csv'] = csv_item

        #  Excel
        ip = ItemProperties(
            title=f"data_{uuid.uuid4().hex[:3]}",
            item_type=ItemTypeEnum.MICROSOFT_EXCEL,
        )
        excel_item = folder.add(
            item_properties=ip,
            file=os.path.join(cls.source_path, "excel_dataset.xlsx"),
        ).result()
        cls.data['excel'] = excel_item

        ip = ItemProperties(
            title=f"data_{uuid.uuid4().hex[:3]}",
            item_type=ItemTypeEnum.SERVICE_DEFINITION,
        )
        sd_item = folder.add(
            item_properties=ip,
            file=os.path.join(
                cls.source_path,
                "Fortune_10_Corporate_HQ_attachments_AGOL.sd",
            ),
        ).result()
        cls.data['sd'] = sd_item

    # @unittest.skip("i work")
    def test_publish_csv(self):
        if "csv" in self.data:
            self.pitems.append(publish(item=self.data['csv']).result())

    # @unittest.skip("i work")
    def test_publish_excel(self):
        if "excel" in self.data:
            self.pitems.append(publish(item=self.data['excel']).result())

    # @unittest.skip("i work")
    def test_publish_fgdb(self):
        if "fgdb" in self.data:
            self.pitems.append(publish(item=self.data['fgdb']).result())

    # @unittest.skip("i work")
    def test_publish_sd(self):
        if "sd" in self.data:
            self.pitems.append(publish(item=self.data['sd']).result())

    # @unittest.skip("i work")
    def test_publish_geopackage(self):
        if "gpkg" in self.data:
            self.pitems.append(publish(item=self.data['gpkg']).result())

    # @unittest.skip("i work")
    def test_publish_shapefile(self):
        if "shapefile" in self.data:
            self.pitems.append(publish(item=self.data['shapefile']).result())

    @classmethod
    def tearDownClass(cls):
        for i in cls.pitems:
            try:
                i.delete(permanent=True)
            except:
                print(i)
        for k, v in cls.data.items():
            try:
                v.delete(permanent=True)
            except:
                print(f"{k} in {v}")


if __name__ == "__main__":
    unittest.main()
