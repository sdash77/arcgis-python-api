#-------------------------------------------------------------------------------
# Name:        clone items tests
# Purpose:     Sanity tests for ArcGIS Python API
#-------------------------------------------------------------------------------
import sys
#sys.path.insert(0, r"C:\SVN\achapkowski_geosaurus_fork\src")
import unittest, pytest
import os
from pathlib import Path
from random import uniform
import json
import datetime, time
from arcgis.gis import GIS
from arcgis.gis import ContentManager
from arcgis.features import Feature
from arcgis.mapping import WebMap

profiles = [
    'your_online_profile',
    'your_enterprise_profile',
    'your_ent_admin_profile'
]

flc = """{"layers":[{"layerDefinition":{"currentVersion":10.8,"id":0,"name":"gcemetry","type":"Feature Layer","displayField":null,"description":"","copyrightText":"","defaultVisibility":true,"relationships":[],"isDataVersioned":false,"supportsCalculate":true,"supportsASyncCalculate":true,"supportsAttachmentsByUploadId":true,"supportsRollbackOnFailureParameter":true,"supportsStatistics":true,"supportsAdvancedQueries":true,"supportsValidateSql":true,"supportsCoordinatesQuantization":true,"supportsFieldDescriptionProperty":true,"advancedQueryCapabilities":{"supportsReturningQueryExtent":true,"supportsStatistics":true,"supportsDistinct":true,"supportsPagination":true,"supportsOrderBy":true,"supportsQueryWithDistance":true,"supportsLod":false,"supportsPaginationOnAggregatedQueries":true,"supportsQueryWithResultType":true,"supportsCountDistinct":true,"supportsReturningGeometryCentroid":false,"supportsHavingClause":true,"supportsQueryWithLodSR":false,"supportsTopFeaturesQuery":false,"supportsOrderByOnlyOnLayerFields":false,"supportsPercentileStatistics":true,"supportsQueryAttachments":true,"supportsQueryAttachmentsWithReturnUrl":true,"supportsQueryWithDatumTransformation":true},"useStandardizedQueries":true,"geometryType":"esriGeometryPoint","minScale":0,"maxScale":0,"extent":{"xmin":-1.853756604466763E7,"ymin":777381.5261038442,"xmax":1.761092897969119E7,"ymax":1.1495136504278956E7,"spatialReference":{"wkid":102100,"latestWkid":3857}},"drawingInfo":{"renderer":{"type":"simple","symbol":{"type":"esriPMS","url":"RedSphere.png","imageData":"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","contentType":"image/png","width":15,"height":15}}},"allowGeometryUpdates":true,"hasAttachments":false,"htmlPopupType":"esriServerHTMLPopupTypeNone","hasMetadata":true,"hasM":false,"hasZ":false,"objectIdField":"objectid","uniqueIdField":{"name":"OBJECTID","isSystemMaintained":true},"globalIdField":"globalid","typeIdField":"","fields":[{"name":"objectid","type":"esriFieldTypeOID","alias":"OBJECTID","nullable":false,"editable":false,"domain":null,"defaultValue":null},{"name":"name","type":"esriFieldTypeString","alias":"NAME","length":120,"nullable":true,"editable":true,"domain":null,"defaultValue":null},{"name":"stctyfips","type":"esriFieldTypeString","alias":"STCTYFIPS","length":5,"nullable":true,"editable":true,"domain":null,"defaultValue":null},{"name":"elev_meter","type":"esriFieldTypeSmallInteger","alias":"ELEV_METER","nullable":true,"editable":true,"domain":null,"defaultValue":null},{"name":"globalid","type":"esriFieldTypeGlobalID","alias":"GlobalID","length":38,"nullable":false,"editable":false,"domain":null,"defaultValue":"NEWID() WITH VALUES"}],"indexes":[{"name":"uuid_127","fields":"globalid","isAcsending":true,"isUnique":true,"description":""},{"name":"a105_ix1","fields":"shape","isAcsending":true,"isUnique":false,"description":""},{"name":"r127_sde_rowid_uk","fields":"objectid","isAcsending":true,"isUnique":false,"description":""}],"types":[],"templates":[{"name":"New Feature","description":"","drawingTool":"esriFeatureEditToolPoint","prototype":{"attributes":{"name":null,"stctyfips":null,"elev_meter":null}}}],"supportedQueryFormats":"JSON, geoJSON, PBF","hasStaticData":true,"maxRecordCount":2000,"standardMaxRecordCount":16000,"standardMaxRecordCountNoGeometry":16000,"tileMaxRecordCount":4000,"maxRecordCountFactor":1,"capabilities":"Query,Sync","hasGeometryProperties":true,"editFieldsInfo":null,"allowUpdateWithoutMValues":true,"advancedEditingCapabilities":{"supportedSqlFormatsInCalculate":["standard"]},"supportsApplyEditsWithGlobalIds":true,"supportsValidateSQL":true,"syncCanReturnChanges":true,"supportsAsyncDelete":true,"sqlParserVersion":"PG_10.6.1"},"featureSet":{"geometryType":"esriGeometryPoint","spatialReference":{"wkid":102100,"latestWkid":3857},"features":[]}}],"showLegend":true}"""


########################################################################
class TestCloneItems(unittest.TestCase):
    """tests simple clone items workflow for sanity reasons"""
    
    def test_portal_to_agol(self):
        """tests cloning from Portal to AGOL"""
        gis_objs = {
            'enterprise' : GIS(profile=profiles[1], verify_cert=False),
        }
        gis_source = gis_objs['enterprise']
        csource = gis_source.content
        for it in csource.search("clone_item_test_*"):
            it.delete()
        for it in csource.search("test_point_cloning*"):
            it.delete()      
        isinstance(csource, ContentManager)
        item = csource.add(item_properties={'title' : "clone_item_test_" + f"{int(time.time())}"[:10],
                                            "type":"Feature Collection",
                                            'tags' : "erase me",
                                            "text" : flc})
        pitem = item.publish()
        wm = WebMap()
        wm.add_layer(pitem.layers[0])
        saved_map = wm.save(item_properties={'title':'test_point_cloning',
                         'snippet':'Map',
                         'tags':['automation', 'erase me', 'python']})
        gis_dest =  GIS(profile=profiles[0], verify_cert=False)
        for it in gis_dest.content.search("clone_item_test_*"):
            it.delete()        
        for it in gis_dest.content.search("test_point_cloning*"):
            it.delete()            
        res = gis_dest.content.clone_items([saved_map])
        assert len(res) > 0
        for i in res:
            i.delete()
        pitem.delete()
        item.delete()
        saved_map.delete()
        
        
    def test_agol_to_portal(self):
        """tests cloning from AGOL to Portal"""
        gis_objs = {
            'agol' : GIS(profile=profiles[0], verify_cert=False),
        }
        gis_source = gis_objs['agol']
        csource = gis_source.content
        for it in csource.search("clone_item_test_*"):
            it.delete()
        for it in csource.search("test_point_cloning*"):
            it.delete()        
        isinstance(csource, ContentManager)
        item = csource.add(item_properties={'title' : "clone_item_test_" + f"{int(time.time())}"[:10],
                                            "type":"Feature Collection",
                                            'tags' : "erase me",
                                            "text" : flc})
        pitem = item.publish()
        wm = WebMap()
        wm.add_layer(pitem.layers[0])
        saved_map = wm.save(item_properties={'title':'test_point_cloning',
                         'snippet':'Map',
                         'tags':['automation', 'erase me', 'python']})
        gis_dest =  GIS(profile=profiles[1], verify_cert=False)
        for it in gis_dest.content.search("clone_item_test_*"):
            it.delete()        
        for it in gis_dest.content.search("test_point_cloning*"):
            it.delete()        
        res = gis_dest.content.clone_items([saved_map])
        assert len(res) > 0
        for i in res:
            i.delete()
        pitem.delete()
        item.delete()
        saved_map.delete()

        def ent_to_ent(self):
            """tests cloning from Enterprise to Enterprise"""
            gis_objs = {
                'ent_admin': GIS(profile=profiles[2], verify_cert=False),
            }
            gis_source = gis_objs['ent_admin']
            csource = gis_source.content
            for it in csource.search("clone_item_test_*"):
                it.delete()
            for it in csource.search("test_point_cloning*"):
                it.delete()
            isinstance(csource, ContentManager)
            item = csource.add(item_properties={'title': "clone_item_test_" + f"{int(time.time())}"[:10],
                                                "type": "Feature Collection",
                                                'tags': "erase me",
                                                "text": flc})
            pitem = item.publish()
            wm = WebMap()
            wm.add_layer(pitem.layers[0])
            saved_map = wm.save(item_properties={'title': 'test_point_cloning',
                                                 'snippet': 'Map',
                                                 'tags': ['automation', 'erase me', 'python']})
            gis_dest = GIS(profile=profiles[1], verify_cert=False)
            for it in gis_dest.content.search("clone_item_test_*"):
                it.delete()
            for it in gis_dest.content.search("test_point_cloning* and owner:" + gis_dest.users.me.username):
                it.delete()
            res = gis_dest.content.clone_items([saved_map])
            assert len(res) > 0
            for i in res:
                i.delete()
            pitem.delete()
            item.delete()
            saved_map.delete()

        def ent_to_ent_vw(self):
            gis_objs = {
                'ent_admin': GIS(profile=profiles[2], verify_cert=False),
            }
            gis_source = gis_objs['ent_admin']
            csource = gis_source.content
            isinstance(csource, ContentManager)
            item = csource.add(item_properties={'title': "clone_item_test_" + f"{int(time.time())}"[:10],
                                                "type": "Feature Collection",
                                                'tags': "erase me",
                                                "text": flc})
            pitem = item.publish()
            # Add features to hosted feature layer so can create a view with subset of features
            random_ext = {"xmin": -9442643.5519,
                          "ymin": 4636846.9513999997,
                          "xmax": -8963158.0244,
                          "ymax": 5157437.8351999997,
                          "spatialReference": {"wkid": 102100, "latestWkid": 3857}}
            for i in range(3):
                pt_geom = Point({"x": uniform(random_ext["xmin"], random_ext["xmax"]),
                                 "y": uniform(random_ext["ymin"], random_ext["ymax"]),
                                 "spatialReference": random_ext["spatialReference"]})
                pt_attr = deepcopy({f["name"]: "" for f in pitem.layers[0].properties.fields})
                pt_attr["objectid"] = i + 1
                r = str(randrange(1, 175, 2))
                if len(r) == 2:
                    r = "0" + r
                if len(r) == 1:
                    r = "00" + r
                pt_attr["stctyfips"] = "39" + r
                pt_attr["name"] = "city" + str(i + 1)
                pt_attr["elev_meter"] = int(uniform(1, 470))
                new_feat = Feature(geometry=pt_geom, attributes=pt_attr)
                pitem.layers[0].edit_features(adds=[new_feat])
            pitem_mgr = pitem.layers[0].container.manager
            flc_view = pitem_mgr.create_view(name="clone_vw_test_" + f"{int(time.time())}"[:10],
                                             spatial_reference=dict(pitem_mgr.properties.spatialReference),
                                             capabilities="Query,Create,Update,Delete,Editing")
            flc_view.layers[0].manager.update_definition({"viewDefinitionQuery": "objectid < 2)"})
            gis_dest = GIS(profile=profiles[1], verify_cert=False)
            # delete any views owned by user who will run the clone
            for it in gis_dest.content.search("clone_vw_test_* AND owner:" + gis_dest.users.me.username):
                it.delete()
            res = gis_dest.content.clone_items([flc_view])
            assert len(res) > 0
            # separate the view and the hosted feature layer in the response
            res_vw = [vw for vw in res if "View Service" in vw.typeKeywords][0]
            res_it = [it for it in res if not "View Service" in it.typeKeywords][0]
            # delete the cloned view and hosted feature layer items
            res_vw.delete()
            res_it.delete()
            # delete the original view, hosted feature layer, and feature layer items
            flc_view.delete()
            pitem.delete()
            item.delete()

if __name__ == "__main__":
    unittest.main()