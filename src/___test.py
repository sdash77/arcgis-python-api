from arcgis._impl.portalpy import _ArcGISConnection

if __name__ == "__main__":
    a = _ArcGISConnection(baseurl="https://achap.esri.com/portal/sharing/rest",
                          username="admin",
                          password="fujifuji1", ensure_ascii=False)
    print (a.get(path="community/users/admin/tags?f=json", try_json=True))
    print (a.get(path="?f=json", try_json=True))
    print (a.post(path="", postdata={"f": "json"}))
    print (a.post(path="/community/users/admin", postdata={"f": "json"}))
    #https://achap.esri.com/portal/sharing/rest/community/users/admin/update
    print (a.post(path="community/users/admin/update", postdata={"f": "json", "lastname" : "geosaury"}))