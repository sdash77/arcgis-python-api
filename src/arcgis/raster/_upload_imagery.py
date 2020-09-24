import os
import time

import arcgis as _arcgis

try:
    from azure.storage.blob import ContainerClient
except:
    pass


def _generate_direct_access_url(gis=None):
    gis = _arcgis.env.active_gis if gis is None else gis
    url = "%s/sharing/rest/content/users/%s/generateDirectAccessUrl" % (gis._portal.url,
                                                                 gis._username)
    params = {"f" : "json", "storeType":"rasterStore"}
    res = gis._portal.con.post(url, params)
    if isinstance(res, dict):
        if "url" in res.keys():
            return res["url"]
        else:
            raise RuntimeError("Couldn't generate direct access url")
    else:
        raise RuntimeError("Couldn't generate direct access url")
    
def upload_imagery(files, gis=None):
    sas_url = _generate_direct_access_url(gis)

    if not isinstance(files,list):
        files = [files]

    url_list = []
    for file in files:
        current_time = int(time.time())
        prefix =  "_images/"+str(current_time)+"/"
        blobname = prefix+os.path.basename(file)

        container = ContainerClient.from_container_url(sas_url)
        blob=container.get_blob_client(blobname)

        with open(file, "rb") as data:
            blob.upload_blob(data, blob_type="BlockBlob")

        url = blob.url.rsplit("?", 1)[0]
        url_list.append(url)

    if len(url_list) == 1:
        return url_list[0]
    return url_list


