import sys

sys.path.insert(0, r"C:\ipython_workfolder\geosaurus\src")
import datetime
import unittest
import pandas as pd
from arcgis.gis import GIS, Item
from arcgis.features import FeatureLayer
from arcgis.features.find_locations import find_existing_locations

data = [
    {
        "FID": 1,
        "NAME": "MARKET FRESH GRILL CAFE",
        "ADDR": "221 W ORANGETHORPE AVE",
        "PHONE": "(714) 528-1977",
        "DAYS": "Mon - Sun",
        "HOURS": "7 AM - 9 PM",
        "OPTIONS": "Takeout, Delivery, Drive-Thru",
        "DISCOUNTS": "(School, Fire/Police, Senior Discounts)",
        "NOTES": "*Grubhub, Postmates, Doordash",
        "DEL_OPTS": "Grubhub, Postmates, Doordash",
        "TYPE": "American",
        "WEBSITE": "https://marketfreshgrillcafe.com",
        "Doordash": " ",
        "Grubhub": "https://www.grubhub.com/restaurant/market-fresh-grill-cafe-221-w-orangethorpe-ave-placentia/1290830",
        "Postmates": "https://postmates.com/merchant/toms-place-placentia",
        "Other": " ",
        "OUTDINE": "Open",
        "SHAPE": {
            "x": -13121824.265019992,
            "y": 4010311.1421616497,
            "spatialReference": {"wkid": 102100, "latestWkid": 3857},
        },
    },
    {
        "FID": 2,
        "NAME": "301 CAFE",
        "ADDR": "301 W SANTA FE AVE",
        "PHONE": "(714) 996-8001",
        "DAYS": "Mon - Sat",
        "HOURS": "10 AM - 9:30 PM",
        "OPTIONS": "Takeout, 3rd party Delivery",
        "DISCOUNTS": "None",
        "NOTES": " ",
        "DEL_OPTS": "Doordash",
        "TYPE": "Mexican",
        "WEBSITE": " ",
        "Doordash": "https://www.doordash.com/store/301-cafe-placentia-723324/en-US",
        "Grubhub": " ",
        "Postmates": " ",
        "Other": " ",
        "OUTDINE": "Open",
        "SHAPE": {
            "x": -13121629.643094601,
            "y": 4011297.297220264,
            "spatialReference": {"wkid": 102100, "latestWkid": 3857},
        },
    },
    {
        "FID": 3,
        "NAME": "Q TORTAS",
        "ADDR": "220 S BRADFORD AVE",
        "PHONE": "(714) 993-3270",
        "DAYS": "Tue - Friday, Sat - Sun",
        "HOURS": "11 AM - 8 PM, 9 AM - 8 PM",
        "OPTIONS": "Takeout",
        "DISCOUNTS": "None",
        "NOTES": " ",
        "DEL_OPTS": " ",
        "TYPE": "Mexican",
        "WEBSITE": " ",
        "Doordash": " ",
        "Grubhub": " ",
        "Postmates": " ",
        "Other": " ",
        "OUTDINE": "Open",
        "SHAPE": {
            "x": -13121342.054302571,
            "y": 4011316.8427645396,
            "spatialReference": {"wkid": 102100, "latestWkid": 3857},
        },
    },
    {
        "FID": 4,
        "NAME": "THE WHOLE ENCHILADA",
        "ADDR": "106 E YORBA LINDA BLVD",
        "PHONE": "(714) 961-9123",
        "DAYS": "Mon - Sun",
        "HOURS": "11 AM - 8 PM",
        "OPTIONS": "Takeout, Delivery",
        "DISCOUNTS": "None",
        "NOTES": "*Doordash",
        "DEL_OPTS": "Doordash",
        "TYPE": "Mexican",
        "WEBSITE": "https://wholeenchilada.com",
        "Doordash": "https://www.doordash.com/store/the-whole-enchilada-placentia-56007/en-US",
        "Grubhub": " ",
        "Postmates": " ",
        "Other": " ",
        "OUTDINE": "Open",
        "SHAPE": {
            "x": -13120774.654751526,
            "y": 4013636.1349284584,
            "spatialReference": {"wkid": 102100, "latestWkid": 3857},
        },
    },
    {
        "FID": 5,
        "NAME": "AVALON BAGLES AND BURGERS",
        "ADDR": "174 E YORBA LINDA BLVD",
        "PHONE": "(714) 985-1382",
        "DAYS": "Mon - Sun",
        "HOURS": "7AM - 4 PM",
        "OPTIONS": "Takeout, 3rd party Delivery",
        "DISCOUNTS": "None",
        "NOTES": " ",
        "DEL_OPTS": "Grubhub, Doordash, Seamless",
        "TYPE": "Bagels, Burgers, Sandwiches",
        "WEBSITE": "https://avalonbagelstoburgers.com/",
        "Doordash": "https://www.doordash.com/store/avalon-bagels-to-burgers-placentia-320809/en-US",
        "Grubhub": "https://www.grubhub.com/restaurant/avalon-bagels-to-burgers---placentia-174-e-yorba-linda-blvd-placentia/553124",
        "Postmates": " ",
        "Other": " ",
        "OUTDINE": "Open",
        "SHAPE": {
            "x": -13120516.589507373,
            "y": 4013511.6346839233,
            "spatialReference": {"wkid": 102100, "latestWkid": 3857},
        },
    },
    {
        "FID": 6,
        "NAME": "ISE JAPANESE RESTAURANT",
        "ADDR": "1241 E YORBA LINDA BLVD",
        "PHONE": "(714) 993-6442",
        "DAYS": "Mon - Thur, Fri, Sat",
        "HOURS": "11 AM - 10 PM, 11 AM - 10:30 PM, 11:30 AM - 10 PM",
        "OPTIONS": "Takeout",
        "DISCOUNTS": "None",
        "NOTES": " ",
        "DEL_OPTS": " ",
        "TYPE": "Japanese",
        "WEBSITE": "https://isesushi.wordpress.com",
        "Doordash": " ",
        "Grubhub": " ",
        "Postmates": " ",
        "Other": " ",
        "OUTDINE": "Open",
        "SHAPE": {
            "x": -13117975.00648396,
            "y": 4013952.0928615234,
            "spatialReference": {"wkid": 102100, "latestWkid": 3857},
        },
    },
    {
        "FID": 7,
        "NAME": "COFFEE BEAN & TEA LEAF #392",
        "ADDR": "1188 E YORBA LINDA BLVD",
        "PHONE": "(310) 237-2326",
        "DAYS": "Mon - Sun",
        "HOURS": "6 AM - 6 PM",
        "OPTIONS": "Drive-Thru",
        "DISCOUNTS": "None",
        "NOTES": "657-216-5920",
        "DEL_OPTS": "Postmates",
        "TYPE": "Coffee",
        "WEBSITE": "https://coffeebean.com",
        "Doordash": " ",
        "Grubhub": " ",
        "Postmates": "https://postmates.com/merchant/the-coffee-bean-placentia",
        "Other": " ",
        "OUTDINE": "Open",
        "SHAPE": {
            "x": -13118132.860060971,
            "y": 4013795.8679011846,
            "spatialReference": {"wkid": 102100, "latestWkid": 3857},
        },
    },
    {
        "FID": 8,
        "NAME": "PORKY'S PIZZA",
        "ADDR": "1152 E IMPERIAL HWY",
        "PHONE": "(714) 572-1777",
        "DAYS": "Sun - Thur, Fri - Sat",
        "HOURS": "11 AM - 9 PM, 11 AM - 10 PM",
        "OPTIONS": "Takeout, Delivery",
        "DISCOUNTS": "None",
        "NOTES": "*Ubereats, Postmates, Doordash",
        "DEL_OPTS": "Ubereats, Postmates, Doordash",
        "TYPE": "Pizza",
        "WEBSITE": "https://porkyspizza.com",
        "Doordash": "https://www.doordash.com/store/porky-s-pizza-placentia-16731/en-US",
        "Grubhub": " ",
        "Postmates": " ",
        "Other": " ",
        "OUTDINE": "Open",
        "SHAPE": {
            "x": -13118260.5041459,
            "y": 4015977.511310816,
            "spatialReference": {"wkid": 102100, "latestWkid": 3857},
        },
    },
    {
        "FID": 9,
        "NAME": "FISH IN A BOTTLE",
        "ADDR": "1205 E IMPERIAL HWY",
        "PHONE": "(714) 528-4000",
        "DAYS": "Until this Sunday",
        "HOURS": "11:30 AM - 9:30 PM, Sat 11:30 AM -10:30, Sun 4 PM*",
        "OPTIONS": "Take-out",
        "DISCOUNTS": "None",
        "NOTES": "*Doordash, Postmates, call in orders only, Will n*",
        "DEL_OPTS": "Doordash, Postmates",
        "TYPE": "Sushi",
        "WEBSITE": "http://fish-in-a-bottle-sushi-grill.cafes-usa.com/",
        "Doordash": " ",
        "Grubhub": " ",
        "Postmates": "https://postmates.com/merchant/fish-in-a-bottle-placentia",
        "Other": " ",
        "OUTDINE": "Open",
        "SHAPE": {
            "x": -13118048.480420934,
            "y": 4015961.906490283,
            "spatialReference": {"wkid": 102100, "latestWkid": 3857},
        },
    },
    {
        "FID": 10,
        "NAME": "WINGSTOP #1553",
        "ADDR": "1093 E IMPERIAL HWY",
        "PHONE": "(714) 868-7000",
        "DAYS": "Mon - Sun",
        "HOURS": "10:30 AM - Midnight",
        "OPTIONS": "Delivery, Takeout",
        "DISCOUNTS": "Mondays & Tuesdays 60 cent boneless wings.",
        "NOTES": "*Doordash",
        "DEL_OPTS": "Doordash",
        "TYPE": "Chicken Wings",
        "WEBSITE": "https://wingstop.com",
        "Doordash": "https://www.doordash.com/store/wingstop-placentia-647491/en-US",
        "Grubhub": " ",
        "Postmates": " ",
        "Other": " ",
        "OUTDINE": "Open",
        "SHAPE": {
            "x": -13118439.698197426,
            "y": 4016169.0124437176,
            "spatialReference": {"wkid": 102100, "latestWkid": 3857},
        },
    },
]


profiles = ["your_online_profile", "ent11"]


class TestFindExistingLocation(unittest.TestCase):
    def test_overwrite(self):
        """tests overwriting an Item layer using the context param"""
        for profile in profiles:
            # establish gis connection
            gis = GIS(profile=profile, verify_cert=False)
            print("User: ", gis.users.me.username)

            # create point layer in portal
            sdf = pd.DataFrame(data)
            fs = gis.content.import_data(sdf)
            # gather layers
            point_item = gis.content.get(fs.id)
            assert isinstance(point_item, Item)
            point_layer = point_item.layers[0]
            assert isinstance(point_layer, FeatureLayer)

            # create layer that will be overwritten
            test_id = str(datetime.datetime.now().microsecond)
            output_name = "test_find_existing_location_" + test_id
            print("Creating ", output_name)
            target_item = find_existing_locations(
                input_layers=[point_layer],
                expressions={"operator": "", "layer": 0, "where": "Notes = 'Doordash'"},
                output_name=output_name,
            )
            assert isinstance(target_item, Item)
            target_layer = target_item.layers[0]
            assert isinstance(target_layer, FeatureLayer)

            # perform overwrite
            print("Overwriting target layer")
            overwrite = find_existing_locations(
                input_layers=[point_layer],
                expressions={
                    "operator": "and",
                    "layer": 0,
                    "where": "OUTDINE = 'Open'",
                },
                output_name=target_layer,
                context={"overwrite": True},
            )
            assert isinstance(overwrite, Item)
            assert target_item.id == overwrite.id
            # overwrite should not append. Only one layer should be present
            assert len(target_item.layers) == 1

            # delete items that were added for test purposes
            assert target_item.delete()
            assert fs.delete()


if __name__ == "__main__":
    unittest.main()
