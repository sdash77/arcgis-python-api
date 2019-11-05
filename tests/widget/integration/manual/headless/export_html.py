#RUN THIS CELL, OPEN THE HTML, ASSERT THAT YOU SEE THE LAYERS
from arcgis.gis import GIS
gis = GIS()
map = gis.map(mode="3D")
map.center = {'spatialReference': {'latestWkid': 3857, 'wkid': 102100},
 'x': -12573068.471521234,
 'y': 4473781.887479003,
 'z': 1979.9325366951525}
map.zoom= 15.528381436708822
map.portal_items = ()
item = gis.content.get('dd0889d7ccd340dd876dac12184e99f9')
map.add_layer(item, {"opacity" : 0.7})
map.export_to_html('./exported.html')
print("./exported.html successfully written")
#Open that file in a web browser, you should see the Zion national park layers
