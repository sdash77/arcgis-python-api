import datetime
from arcgis.gis import GIS
g = GIS(profile="widget_test_publisher_credentials")
item_from_agol = g.content.get('bbf5a6899824407697e114556c213139')
m = g.map('USA')
m.add_layer(item_from_agol)
item = m.save({'title':'saved webmap {}'.format(datetime.datetime.now()),
               'snippet':'testing new webscene',
               'tags':'test'})
print("https://arcgis.com/home/item.html?id={}".format(item.id))
