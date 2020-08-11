from arcgis.features.layer import FeatureLayer

from utils.mocks.layers import MockFeatureLayer

def test_update_attachments():
    mfl = MockFeatureLayer()
    oid = 1
    attachment_id = 8
    file_path = "/arbitrary/path.jpg"


    FeatureLayer._update_attachment(mfl, oid, attachment_id, file_path)

    expected_url = f"{mfl.url}/{oid}/updateAttachment"
    expected_postdata = {"f" : "json",
                         "attachmentId" : "8"}
    expected_files = {'attachment' : file_path}


    mfl._con.post.assert_called_with(path = expected_url,
                                     postdata = expected_postdata,
                                     files = expected_files,
                                     token = mfl._token)

def test_update_attachments_dynamic_layer():
    mfl = MockFeatureLayer()
    mfl._dynamic_layer = {"dynamic" : "layer"}
    mfl.url = "https://example.com/server/rest/services/Hosted/" + \
              "CamerTraps/FeatureServer?somethingthatshouldberemoved"
    oid = 1
    attachment_id = 8
    file_path = "/arbitrary/path.jpg"


    FeatureLayer._update_attachment(mfl, oid, attachment_id, file_path)

    expected_url = f"https://example.com/server/rest/services/Hosted/" + \
                   f"CamerTraps/FeatureServer/{oid}/updateAttachment"
    expected_postdata = {"f" : "json",
                         "attachmentId" : "8",
                         "layer" : {"dynamic" : "layer"}}
    expected_files = {'attachment' : file_path}


    mfl._con.post.assert_called_with(path = expected_url,
                                     postdata = expected_postdata,
                                     files = expected_files,
                                     token = mfl._token)

if __name__ == "__main__":
    test_update_attachments_dynamic_layer()