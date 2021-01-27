from arcgis.features.layer import FeatureLayer

from utils.mocks.layers import MockFeatureLayer

_common_postdata = { 'f' : 'json', 
                     'upsert' : True, 
                     'skipUpdates' : False, 
                     'useGlobalIds' : False, 
                     'updateGeometry' : True,  
                     'appendUploadFormat' : 'featureCollection', 
                     'rollbackOnFailure' : False }

def test_upload_item_id():
    item_id = "da78c9fb55bb5e44e44c6f88ee7d4ee4"
    mfl = MockFeatureLayer()
    FeatureLayer.append(mfl, item_id=item_id)

    expected_url = f"{mfl.url}/append"
    expected_postdata =  dict(_common_postdata)
    expected_postdata["appendItemId"] = item_id
    mfl._con.post.assert_called_with(path = expected_url,
                                     postdata = expected_postdata)

def test_append_upload_id():
    upload_id = "da78c9fb55bb5e44e44c6f88ee7d4ee4"
    mfl = MockFeatureLayer()
    FeatureLayer.append(mfl, upload_id=upload_id)

    expected_url = f"{mfl.url}/append"
    expected_postdata =  dict(_common_postdata)
    expected_postdata["appendUploadId"] = upload_id
    mfl._con.post.assert_called_with(path = expected_url,
                                     postdata = expected_postdata)