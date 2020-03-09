import os
import sys
import json
import pytest
import unittest
import pandas as pd
from arcgis.gis import GIS
from urllib.parse import urlparse
from arcgis.geocoding import (Geocoder, #
                              analyze_geocode_input,
                              batch_geocode, #
                              geocode, #
                              geocode_from_items, 
                              get_geocoders, #
                              reverse_geocode, # 
                              suggest) #

#gis = GIS(profile='your_online_profile')
#lyr = gis.content.search("owner:andrew57", "Feature Layer")[0]
#print(lyr.metadata)

data = '[{"street": "777 Brockton Avenue", "city_state_zip": " Abington MA 2351"}, {"street": "30 Memorial Drive", "city_state_zip": " Avon MA 2322"}, {"street": "250 Hartford Avenue", "city_state_zip": " Bellingham MA 2019"}, {"street": "700 Oak Street", "city_state_zip": " Brockton MA 2301"}, {"street": "66-4 Parkhurst Rd", "city_state_zip": " Chelmsford MA 1824"}, {"street": "591 Memorial Dr", "city_state_zip": " Chicopee MA 1020"}, {"street": "55 Brooksby Village Way", "city_state_zip": " Danvers MA 1923"}, {"street": "137 Teaticket Hwy", "city_state_zip": " East Falmouth MA 2536"}, {"street": "42 Fairhaven Commons Way", "city_state_zip": " Fairhaven MA 2719"}, {"street": "374 William S Canning Blvd", "city_state_zip": " Fall River MA 2721"}, {"street": "121 Worcester Rd", "city_state_zip": " Framingham MA 1701"}, {"street": "677 Timpany Blvd", "city_state_zip": " Gardner MA 1440"}, {"street": "337 Russell St", "city_state_zip": " Hadley MA 1035"}, {"street": "295 Plymouth Street", "city_state_zip": " Halifax MA 2338"}, {"street": "1775 Washington St", "city_state_zip": " Hanover MA 2339"}, {"street": "280 Washington Street", "city_state_zip": " Hudson MA 1749"}, {"street": "20 Soojian Dr", "city_state_zip": " Leicester MA 1524"}, {"street": "11 Jungle Road", "city_state_zip": " Leominster MA 1453"}, {"street": "301 Massachusetts Ave", "city_state_zip": " Lunenburg MA 1462"}, {"street": "780 Lynnway", "city_state_zip": " Lynn MA 1905"}, {"street": "70 Pleasant Valley Street", "city_state_zip": " Methuen MA 1844"}, {"street": "830 Curran Memorial Hwy", "city_state_zip": " North Adams MA 1247"}, {"street": "1470 S Washington St", "city_state_zip": " North Attleboro MA 2760"}, {"street": "506 State Road", "city_state_zip": " North Dartmouth MA 2747"}, {"street": "742 Main Street", "city_state_zip": " North Oxford MA 1537"}, {"street": "72 Main St", "city_state_zip": " North Reading MA 1864"}, {"street": "200 Otis Street", "city_state_zip": " Northborough MA 1532"}, {"street": "180 North King Street", "city_state_zip": " Northhampton MA 1060"}, {"street": "555 East Main St", "city_state_zip": " Orange MA 1364"}, {"street": "555 Hubbard Ave-Suite 12", "city_state_zip": " Pittsfield MA 1201"}, {"street": "300 Colony Place", "city_state_zip": " Plymouth MA 2360"}, {"street": "301 Falls Blvd", "city_state_zip": " Quincy MA 2169"}, {"street": "36 Paramount Drive", "city_state_zip": " Raynham MA 2767"}, {"street": "450 Highland Ave", "city_state_zip": " Salem MA 1970"}, {"street": "1180 Fall River Avenue", "city_state_zip": " Seekonk MA 2771"}, {"street": "1105 Boston Road", "city_state_zip": " Springfield MA 1119"}, {"street": "100 Charlton Road", "city_state_zip": " Sturbridge MA 1566"}, {"street": "262 Swansea Mall Dr", "city_state_zip": " Swansea MA 2777"}, {"street": "333 Main Street", "city_state_zip": " Tewksbury MA 1876"}, {"street": "550 Providence Hwy", "city_state_zip": " Walpole MA 2081"}, {"street": "352 Palmer Road", "city_state_zip": " Ware MA 1082"}, {"street": "3005 Cranberry Hwy Rt 6 28", "city_state_zip": " Wareham MA 2538"}, {"street": "250 Rt 59", "city_state_zip": " Airmont NY 10901"}, {"street": "141 Washington Ave Extension", "city_state_zip": " Albany NY 12205"}, {"street": "13858 Rt 31 W", "city_state_zip": " Albion NY 14411"}, {"street": "2055 Niagara Falls Blvd", "city_state_zip": " Amherst NY 14228"}, {"street": "101 Sanford Farm Shpg Center", "city_state_zip": " Amsterdam NY 12010"}, {"street": "297 Grant Avenue", "city_state_zip": " Auburn NY 13021"}, {"street": "4133 Veterans Memorial Drive", "city_state_zip": " Batavia NY 14020"}, {"street": "6265 Brockport Spencerport Rd", "city_state_zip": " Brockport NY 14420"}, {"street": "5399 W Genesse St", "city_state_zip": " Camillus NY 13031"}, {"street": "3191 County rd 10", "city_state_zip": " Canandaigua NY 14424"}, {"street": "30 Catskill", "city_state_zip": " Catskill NY 12414"}, {"street": "161 Centereach Mall", "city_state_zip": " Centereach NY 11720"}, {"street": "3018 East Ave", "city_state_zip": " Central Square NY 13036"}, {"street": "100 Thruway Plaza", "city_state_zip": " Cheektowaga NY 14225"}, {"street": "8064 Brewerton Rd", "city_state_zip": " Cicero NY 13039"}, {"street": "5033 Transit Road", "city_state_zip": " Clarence NY 14031"}, {"street": "3949 Route 31", "city_state_zip": " Clay NY 13041"}, {"street": "139 Merchant Place", "city_state_zip": " Cobleskill NY 12043"}, {"street": "85 Crooked Hill Road", "city_state_zip": " Commack NY 11725"}, {"street": "872 Route 13", "city_state_zip": " Cortlandville NY 13045"}, {"street": "279 Troy Road", "city_state_zip": " East Greenbush NY 12061"}, {"street": "2465 Hempstead Turnpike", "city_state_zip": " East Meadow NY 11554"}, {"street": "6438 Basile Rowe", "city_state_zip": " East Syracuse NY 13057"}, {"street": "25737 US Rt 11", "city_state_zip": " Evans Mills NY 13637"}, {"street": "901 Route 110", "city_state_zip": " Farmingdale NY 11735"}, {"street": "2400 Route 9", "city_state_zip": " Fishkill NY 12524"}, {"street": "10401 Bennett Road", "city_state_zip": " Fredonia NY 14063"}, {"street": "1818 State Route 3", "city_state_zip": " Fulton NY 13069"}, {"street": "4300 Lakeville Road", "city_state_zip": " Geneseo NY 14454"}, {"street": "990 Route 5 20", "city_state_zip": " Geneva NY 14456"}, {"street": "311 RT 9W", "city_state_zip": " Glenmont NY 12077"}, {"street": "200 Dutch Meadows Ln", "city_state_zip": " Glenville NY 12302"}, {"street": "100 Elm Ridge Center Dr", "city_state_zip": " Greece NY 14626"}, {"street": "1549 Rt 9", "city_state_zip": " Halfmoon NY 12065"}, {"street": "5360 Southwestern Blvd", "city_state_zip": " Hamburg NY 14075"}, {"street": "103 North Caroline St", "city_state_zip": " Herkimer NY 13350"}, {"street": "1000 State Route 36", "city_state_zip": " Hornell NY 14843"}, {"street": "1400 County Rd 64", "city_state_zip": " Horseheads NY 14845"}, {"street": "135 Fairgrounds Memorial Pkwy", "city_state_zip": " Ithaca NY 14850"}, {"street": "2 Gannett Dr", "city_state_zip": " Johnson City NY 13790"}, {"street": "233 5th Ave Ext", "city_state_zip": " Johnstown NY 12095"}, {"street": "601 Frank Stottile Blvd", "city_state_zip": " Kingston NY 12401"}, {"street": "350 E Fairmount Ave", "city_state_zip": " Lakewood NY 14750"}, {"street": "4975 Transit Rd", "city_state_zip": " Lancaster NY 14086"}, {"street": "579 Troy-Schenectady Road", "city_state_zip": " Latham NY 12110"}, {"street": "5783 So Transit Road", "city_state_zip": " Lockport NY 14094"}, {"street": "7155 State Rt 12 S", "city_state_zip": " Lowville NY 13367"}, {"street": "425 Route 31", "city_state_zip": " Macedon NY 14502"}, {"street": "3222 State Rt 11", "city_state_zip": " Malone NY 12953"}, {"street": "200 Sunrise Mall", "city_state_zip": " Massapequa NY 11758"}, {"street": "43 Stephenville St", "city_state_zip": " Massena NY 13662"}, {"street": "750 Middle Country Road", "city_state_zip": " Middle Island NY 11953"}, {"street": "470 Route 211 East", "city_state_zip": " Middletown NY 10940"}, {"street": "3133 E Main St", "city_state_zip": " Mohegan Lake NY 10547"}, {"street": "288 Larkin", "city_state_zip": " Monroe NY 10950"}, {"street": "41 Anawana Lake Road", "city_state_zip": " Monticello NY 12701"}, {"street": "4765 Commercial Drive", "city_state_zip": " New Hartford NY 13413"}, {"street": "1201 Rt 300", "city_state_zip": " Newburgh NY 12550"}, {"street": "255 W Main St", "city_state_zip": " Avon CT 6001"}, {"street": "120 Commercial Parkway", "city_state_zip": " Branford CT 6405"}, {"street": "1400 Farmington Ave", "city_state_zip": " Bristol CT 6010"}, {"street": "161 Berlin Road", "city_state_zip": " Cromwell CT 6416"}, {"street": "67 Newton Rd", "city_state_zip": " Danbury CT 6810"}, {"street": "656 New Haven Ave", "city_state_zip": " Derby CT 6418"}, {"street": "69 Prospect Hill Road", "city_state_zip": " East Windsor CT 6088"}, {"street": "150 Gold Star Hwy", "city_state_zip": " Groton CT 6340"}, {"street": "900 Boston Post Road", "city_state_zip": " Guilford CT 6437"}, {"street": "2300 Dixwell Ave", "city_state_zip": " Hamden CT 6514"}, {"street": "495 Flatbush Ave", "city_state_zip": " Hartford CT 6106"}, {"street": "180 River Rd", "city_state_zip": " Lisbon CT 6351"}, {"street": "420 Buckland Hills Dr", "city_state_zip": " Manchester CT 6040"}, {"street": "1365 Boston Post Road", "city_state_zip": " Milford CT 6460"}, {"street": "1100 New Haven Road", "city_state_zip": " Naugatuck CT 6770"}, {"street": "315 Foxon Blvd", "city_state_zip": " New Haven CT 6513"}, {"street": "164 Danbury Rd", "city_state_zip": " New Milford CT 6776"}, {"street": "3164 Berlin Turnpike", "city_state_zip": " Newington CT 6111"}, {"street": "474 Boston Post Road", "city_state_zip": " North Windham CT 6256"}, {"street": "650 Main Ave", "city_state_zip": " Norwalk CT 6851"}, {"street": "680 Connecticut Avenue", "city_state_zip": " Norwalk CT 6854"}, {"street": "220 Salem Turnpike", "city_state_zip": " Norwich CT 6360"}, {"street": "655 Boston Post Rd", "city_state_zip": " Old Saybrook CT 6475"}, {"street": "625 School Street", "city_state_zip": " Putnam CT 6260"}, {"street": "80 Town Line Rd", "city_state_zip": " Rocky Hill CT 6067"}, {"street": "465 Bridgeport Avenue", "city_state_zip": " Shelton CT 6484"}, {"street": "235 Queen St", "city_state_zip": " Southington CT 6489"}, {"street": "150 Barnum Avenue Cutoff", "city_state_zip": " Stratford CT 6614"}, {"street": "970 Torringford Street", "city_state_zip": " Torrington CT 6790"}, {"street": "844 No Colony Road", "city_state_zip": " Wallingford CT 6492"}, {"street": "910 Wolcott St", "city_state_zip": " Waterbury CT 6705"}, {"street": "155 Waterford Parkway No", "city_state_zip": " Waterford CT 6385"}, {"street": "515 Sawmill Road", "city_state_zip": " West Haven CT 6516"}, {"street": "2473 Hackworth Road", "city_state_zip": " Adamsville AL 35005"}, {"street": "630 Coonial Promenade Pkwy", "city_state_zip": " Alabaster AL 35007"}, {"street": "2643 Hwy 280 West", "city_state_zip": " Alexander City AL 35010"}, {"street": "540 West Bypass", "city_state_zip": " Andalusia AL 36420"}, {"street": "5560 Mcclellan Blvd", "city_state_zip": " Anniston AL 36206"}, {"street": "1450 No Brindlee Mtn Pkwy", "city_state_zip": " Arab AL 35016"}, {"street": "1011 US Hwy 72 East", "city_state_zip": " Athens AL 35611"}, {"street": "973 Gilbert Ferry Road Se", "city_state_zip": " Attalla AL 35954"}, {"street": "1717 South College Street", "city_state_zip": " Auburn AL 36830"}, {"street": "701 Mcmeans Ave", "city_state_zip": " Bay Minette AL 36507"}, {"street": "750 Academy Drive", "city_state_zip": " Bessemer AL 35022"}, {"street": "312 Palisades Blvd", "city_state_zip": " Birmingham AL 35209"}, {"street": "1600 Montclair Rd", "city_state_zip": " Birmingham AL 35210"}, {"street": "5919 Trussville Crossings Pkwy", "city_state_zip": " Birmingham AL 35235"}, {"street": "9248 Parkway East", "city_state_zip": " Birmingham AL 35206"}, {"street": "1972 Hwy 431", "city_state_zip": " Boaz AL 35957"}, {"street": "10675 Hwy 5", "city_state_zip": " Brent AL 35034"}, {"street": "2041 Douglas Avenue", "city_state_zip": " Brewton AL 36426"}, {"street": "5100 Hwy 31", "city_state_zip": " Calera AL 35040"}, {"street": "1916 Center Point Rd", "city_state_zip": " Center Point AL 35215"}, {"street": "1950 W Main St", "city_state_zip": " Centre AL 35960"}, {"street": "16077 Highway 280", "city_state_zip": " Chelsea AL 35043"}, {"street": "1415 7Th Street South", "city_state_zip": " Clanton AL 35045"}, {"street": "626 Olive Street Sw", "city_state_zip": " Cullman AL 35055"}, {"street": "27520 Hwy 98", "city_state_zip": " Daphne AL 36526"}, {"street": "2800 Spring Avn SW", "city_state_zip": " Decatur AL 35603"}, {"street": "969 Us Hwy 80 West", "city_state_zip": " Demopolis AL 36732"}, {"street": "3300 South Oates Street", "city_state_zip": " Dothan AL 36301"}, {"street": "4310 Montgomery Hwy", "city_state_zip": " Dothan AL 36303"}, {"street": "600 Boll Weevil Circle", "city_state_zip": " Enterprise AL 36330"}, {"street": "3176 South Eufaula Avenue", "city_state_zip": " Eufaula AL 36027"}, {"street": "7100 Aaron Aronov Drive", "city_state_zip": " Fairfield AL 35064"}, {"street": "10040 County Road 48", "city_state_zip": " Fairhope AL 36533"}, {"street": "3186 Hwy 171 North", "city_state_zip": " Fayette AL 35555"}, {"street": "3100 Hough Rd", "city_state_zip": " Florence AL 35630"}, {"street": "2200 South Mckenzie St", "city_state_zip": " Foley AL 36535"}, {"street": "2001 Glenn Bldv Sw", "city_state_zip": " Fort Payne AL 35968"}, {"street": "340 East Meighan Blvd", "city_state_zip": " Gadsden AL 35903"}, {"street": "890 Odum Road", "city_state_zip": " Gardendale AL 35071"}, {"street": "1608 W Magnolia Ave", "city_state_zip": " Geneva AL 36340"}, {"street": "501 Willow Lane", "city_state_zip": " Greenville AL 36037"}, {"street": "170 Fort Morgan Road", "city_state_zip": " Gulf Shores AL 36542"}, {"street": "11697 US Hwy 431", "city_state_zip": " Guntersville AL 35976"}, {"street": "42417 Hwy 195", "city_state_zip": " Haleyville AL 35565"}, {"street": "1706 Military Street South", "city_state_zip": " Hamilton AL 35570"}, {"street": "1201 Hwy 31 NW", "city_state_zip": " Hartselle AL 35640"}, {"street": "209 Lakeshore Parkway", "city_state_zip": " Homewood AL 35209"}, {"street": "2780 John Hawkins Pkwy", "city_state_zip": " Hoover AL 35244"}, {"street": "5335 Hwy 280 South", "city_state_zip": " Hoover AL 35242"}, {"street": "1007 Red Farmer Drive", "city_state_zip": " Hueytown AL 35023"}, {"street": "2900 S Mem PkwyDrake Ave", "city_state_zip": " Huntsville AL 35801"}, {"street": "11610 Memorial Pkwy South", "city_state_zip": " Huntsville AL 35803"}, {"street": "2200 Sparkman Drive", "city_state_zip": " Huntsville AL 35810"}, {"street": "330 Sutton Rd", "city_state_zip": " Huntsville AL 35763"}, {"street": "6140A Univ Drive", "city_state_zip": " Huntsville AL 35806"}, {"street": "4206 N College Ave", "city_state_zip": " Jackson AL 36545"}, {"street": "1625 Pelham South", "city_state_zip": " Jacksonville AL 36265"}, {"street": "1801 Hwy 78 East", "city_state_zip": " Jasper AL 35501"}, {"street": "8551 Whitfield Ave", "city_state_zip": " Leeds AL 35094"}, {"street": "8650 Madison Blvd", "city_state_zip": " Madison AL 35758"}, {"street": "145 Kelley Blvd", "city_state_zip": " Millbrook AL 36054"}, {"street": "1970 S University Blvd", "city_state_zip": " Mobile AL 36609"}, {"street": "6350 Cottage Hill Road", "city_state_zip": " Mobile AL 36609"}, {"street": "101 South Beltline Highway", "city_state_zip": " Mobile AL 36606"}, {"street": "2500 Dawes Road", "city_state_zip": " Mobile AL 36695"}, {"street": "5245 Rangeline Service Rd", "city_state_zip": " Mobile AL 36619"}, {"street": "685 Schillinger Rd", "city_state_zip": " Mobile AL 36695"}, {"street": "3371 S Alabama Ave", "city_state_zip": " Monroeville AL 36460"}, {"street": "10710 Chantilly Pkwy", "city_state_zip": " Montgomery AL 36117"}, {"street": "3801 Eastern Blvd", "city_state_zip": " Montgomery AL 36116"}, {"street": "6495 Atlanta Hwy", "city_state_zip": " Montgomery AL 36117"}, {"street": "851 Ann St", "city_state_zip": " Montgomery AL 36107"}, {"street": "15445 Highway 24", "city_state_zip": " Moulton AL 35650"}, {"street": "517 West Avalon Ave", "city_state_zip": " Muscle Shoals AL 35661"}, {"street": "5710 Mcfarland Blvd", "city_state_zip": " Northport AL 35476"}, {"street": "2453 2Nd Avenue East", "city_state_zip": " Oneonta AL 35121  205-625-647"}, {"street": "2900 Pepperrell Pkwy", "city_state_zip": " Opelika AL 36801"}, {"street": "92 Plaza Lane", "city_state_zip": " Oxford AL 36203"}, {"street": "1537 Hwy 231 South", "city_state_zip": " Ozark AL 36360"}, {"street": "2181 Pelham Pkwy", "city_state_zip": " Pelham AL 35124"}, {"street": "165 Vaughan Ln", "city_state_zip": " Pell City AL 35125"}, {"street": "3700 Hwy 280-431 N", "city_state_zip": " Phenix City AL 36867"}, {"street": "1903 Cobbs Ford Rd", "city_state_zip": " Prattville AL 36066"}, {"street": "4180 Us Hwy 431", "city_state_zip": " Roanoke AL 36274"}, {"street": "13675 Hwy 43", "city_state_zip": " Russellville AL 35653"}, {"street": "1095 Industrial Pkwy", "city_state_zip": " Saraland AL 36571"}, {"street": "24833 Johnt Reidprkw", "city_state_zip": " Scottsboro AL 35768"}, {"street": "1501 Hwy 14 East", "city_state_zip": " Selma AL 36703"}, {"street": "7855 Moffett Rd", "city_state_zip": " Semmes AL 36575"}, {"street": "150 Springville Station Blvd", "city_state_zip": " Springville AL 35146"}, {"street": "690 Hwy 78", "city_state_zip": " Sumiton AL 35148"}, {"street": "41301 US Hwy 280", "city_state_zip": " Sylacauga AL 35150"}, {"street": "214 Haynes Street", "city_state_zip": " Talladega AL 35160"}, {"street": "1300 Gilmer Ave", "city_state_zip": " Tallassee AL 36078"}, {"street": "34301 Hwy 43", "city_state_zip": " Thomasville AL 36784"}, {"street": "1420 Us 231 South", "city_state_zip": " Troy AL 36081"}, {"street": "1501 Skyland Blvd E", "city_state_zip": " Tuscaloosa AL 35405"}, {"street": "3501 20th Av", "city_state_zip": " Valley AL 36854"}, {"street": "1300 Montgomery Highway", "city_state_zip": " Vestavia Hills AL 35216"}, {"street": "4538 Us Hwy 231", "city_state_zip": " Wetumpka AL 36092"}, {"street": "2575 Us Hwy 43", "city_state_zip": " Winfield AL 35594"}]'


ADDRESS_DATA = json.loads(data)
df = pd.DataFrame(ADDRESS_DATA)
"""

geocode - missing 4 parameters


"""
profiles = ['your_enterprise_profile', 'your_online_profile', None]
###########################################################################
class TestAnalyzeGeocodingInput(unittest.TestCase):
    def test_analyze_table_item(self):
        import tempfile
        fp = os.path.join(tempfile.gettempdir(), "data.csv")
        if os.path.isfile(fp):
            os.remove(fp)
        df.to_csv(os.path.join(tempfile.gettempdir(), "data.csv"))
        
        for p in ['your_enterprise_profile']:
            gis = GIS(profile=p, verify_cert=False)  
            for i in gis.content.search("dummy_data_1234"):
                i.delete()
                del i
            item = gis.content.add(data=fp,
                                   item_properties={
                                       "title" : "dummy_data_1234",
                                       "tags" : "A",
                                       "type" : "CSV"
                                   })
            if gis._portal.is_arcgisonline:
                pass
            else:
                gc = None
                l = get_geocoders(gis=gis)
                for gc in get_geocoders(gis=gis):
                    net_loc = urlparse(gis._url.lower()).netloc.lower()
                    if gc.url.lower().find(net_loc) > -1:
                        break
                    else:
                        gc = None
                if gc:
                    res = analyze_geocode_input(geocode_service_url=gc,
                                      input_table_or_item={"itemid" : item.itemid},
                                      input_file_parameters={"fileType":"csv","headerRowExists":"true",
                                                             "columnDelimiter":"","textQualifier":""})
                    assert res
                    assert isinstance(res, dict)
                item.delete()       
###########################################################################
class TestGeocoder(unittest.TestCase):
    """test the geocoder operations"""
    #######################################################################
    def test_create_geocoder_url(self):
        """tests creation of a geocoder from a URL"""
        url = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer"
        for p in profiles:
            g = Geocoder(location=url, gis=GIS(profile=p))
            assert g
            assert g.properties
    #######################################################################
    
    def test_create_geocoder_item(self):
        """tests creation of a geocoder from an item"""
        lu = {
            "your_enterprise_profile" : "00a0a5cbef274e2cbbbdbb47eb1452e7", # Python API Playground
            "your_online_profile" : "305f2e55e67f4389bef269669fc2e284",
            "None" : "305f2e55e67f4389bef269669fc2e284"
        }
        q = '''type:("Geocoding Service")'''
        for p in profiles:
            gis = GIS(profile=p)
            items = gis.content.search(q, outside_org=True)
            if len(items) > 0:
                item = items[0]
                g = Geocoder.fromitem(item)
                assert g
                assert g.properties     
            else:
                print(f"{p} has no geocoders")
    #######################################################################
    
    def test_create_geocoder_from_server(self):
        """tests creating a service from the sample server 6 endpoint"""
        url = "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Locators/Composite_HBR_Asset/GeocodeServer"
        g = Geocoder(url)
        assert g
        assert g.properties
    #######################################################################
    def test_get_geocoders(self):
        """test the operation get_geocoders method"""
        for p in profiles:
            gis = GIS(profile=p)        
            results = get_geocoders(gis)
            assert isinstance(results, list)
            assert len(results) >= 0
            assert all([isinstance(r, Geocoder) for r in results])
    #######################################################################
    def test_reverse_geocode_dict(self):
        """tests the service's reverse geocode method with a geom/dict"""
        geom = {"spatialReference":{"wkid":4326},"x":-75.12646269301656,"y":39.955348161474326}
        for p in profiles:
            gis = GIS(profile=p, verify_cert=False)
            l = get_geocoders(gis)
            assert reverse_geocode(location=geom)
            data =  reverse_geocode(location=geom, distance=1000, out_sr=4326)
            assert data['location']['spatialReference']['wkid'] == 4326
            data =  reverse_geocode(location=geom, out_sr=4326, lang_code='en', return_intersection=True)
            assert data
            data =  reverse_geocode(location=geom, out_sr=4326, lang_code='en', return_intersection=True, distance=1000)
            assert data
            data =  reverse_geocode(location=geom, out_sr=4326, lang_code='en', distance=1000, return_intersection=True, feature_types="PointAddress,Postal")
            assert data
            data =  reverse_geocode(location=geom, out_sr=4326, lang_code='en', distance=1000, return_intersection=True, feature_types=["PointAddress","Postal"])
            assert data
            data =  reverse_geocode(location=geom, out_sr=4326, lang_code='en', distance=1000, return_intersection=True, feature_types=["PointAddress","Postal"], roof_top='rooftop', geocoder=l[0])
            assert data    
    #######################################################################
    def test_reverse_geocode_list(self):
        """tests the service's reverse geocode method using a list of X/Y coordinates"""
        geom = [-75.12646269301656,39.955348161474326]
        for p in profiles:
            gis = GIS(profile=p, verify_cert=False)
            l = get_geocoders(gis)
            assert reverse_geocode(location=geom)
    #######################################################################
    def test_reverse_geocode_pt(self):
        """tests the service's reverse geocode method using a Point Geometry"""
        from arcgis.geometry import Geometry
        geom = Geometry({"spatialReference":{"wkid":4326},"x":-75.12646269301656,"y":39.955348161474326})
        for p in profiles:
            gis = GIS(profile=p, verify_cert=False)
            assert reverse_geocode(location=geom)
    #######################################################################
    def test_geocode(self):
        """tests the service's reverse geocode method using a Point Geometry"""
        for p in profiles:
            gis = GIS(profile=p, verify_cert=False)
            address = "380 New York Street, Redlands, CA 92373"
            g =  geocode(address=address)
            address = "12 York Street, Camden, NJ"
            g1 = geocode(address=address,
                         search_extent='-75.41936574828934,39.89338669631747,-74.8237007702628,39.998669961287526',
                         location=[-75.12153325927608, 39.9460283288025],
                         distance=100,
                         out_sr=3857,
                         category="Address",
                         out_fields="*",
                         max_locations=20,
                         magic_key=None,
                         for_storage=False,
                         geocoder=None,
                         as_featureset=False)         
            g2 = geocode(address=address,
                         search_extent='-75.41936574828934,39.89338669631747,-74.8237007702628,39.998669961287526',
                         location=[-75.12153325927608, 39.9460283288025],
                         distance=100,
                         out_sr=3857,
                         category="Address",
                         out_fields="Rank",
                         max_locations=5,
                         magic_key=None,
                         for_storage=False,
                         geocoder=None,
                         as_featureset=False)     
            g3 = geocode(address=address,
                         search_extent='-75.41936574828934,39.89338669631747,-74.8237007702628,39.998669961287526',
                         location=[-75.12153325927608, 39.9460283288025],
                         distance=100,
                         out_sr=3857,
                         category="Address",
                         out_fields="*",
                         max_locations=5,
                         magic_key=None,
                         for_storage=False,
                         geocoder=get_geocoders(gis)[0],
                         as_featureset=False)     
            g_fs =  geocode(address=address, as_featureset=True)
            g_magic_key = geocode(address="", magic_key='dHA9MSNubT1TdGFyYnVja3Mjc3o9LTExNy4xOTY6MzQuMDU1OTk5OTk5OTk5OTk3I2NzPTcw')
            assert g_magic_key
            assert g1
            assert g
            assert g3
            assert g2
            assert g_fs
            assert 'Rank' in g2[0]['attributes']
    #######################################################################
    def test_suggest(self):
        """tests the suggest operation on geocoder"""
        for p in profiles:
            if p == 'your_online_profile':                
                gis = GIS(profile=p, verify_cert=False)
                s1 = suggest(text='starbu', location=[-117.196,34.056])
                s2 = suggest(text='starbu', location={ "x": -13046165.572, "y": 4036389.847, "spatialReference": { "wkid": 102100 } })
                s3 = suggest(text='starbu', location=[-117.196,34.056], distance=3218.69)
                s4 = suggest(text='starbu', location=[-117.196,34.056], distance=3218.69, category="Address,Postal")
                s5 = suggest(text='starbu', location=[-117.196,34.056], geocoder=get_geocoders(gis=gis)[0])
                assert 'suggestions' in s1
                assert 'suggestions' in s2
                assert 'suggestions' in s3
                assert 'suggestions' in s4
                assert 'suggestions' in s5
                s6 = suggest(text='starbu', location=[-117.196,34.056], country_code="USA")
                s7 = suggest(text='starbu', location=[-117.196,34.056], max_suggestions=10)
                assert len(s7['suggestions']) == 10
                s8 = suggest(text='starbu', location=[-117.196,34.056], search_extent="-104,35.6,-94.32,41")
                s9 = suggest(text='starbu', location=[-117.196,34.056], search_extent={ "xmin" : -109.55, "ymin" : 25.76, "xmax" : -86.39, "ymax" : 49.94, "spatialReference" : {"wkid" : 4326} })
                assert 'suggestions' in s6
                assert 'suggestions' in s7
                assert 'suggestions' in s8
                assert 'suggestions' in s9
    #######################################################################
    def test_batch_geocode_dict(self):
        """tests the batch geocoding operation via list of dictionaries"""
        addresses_dict = [{
                "Address": "380 New York St.",
                "City": "Redlands",
                "Region": "CA",
                "Postal": "92373"
            },{
                "Address": "1 World Way",
                "City": "Los Angeles",
                "Region": "CA",
                "Postal": "90045"
            }]
        for p in ['your_enterprise_profile', 'your_online_profile']:
            gis = GIS(profile=p, verify_cert=False)    
            if gis._portal.is_arcgisonline:
                bc = batch_geocode(addresses=addresses_dict, source_country=None, 
                                   category=None, out_sr=None, geocoder=None, 
                                   as_featureset=False, match_out_of_range=True, 
                                   location_type='street', search_extent=None, 
                                   lang_code='EN', preferred_label_values=None)
                assert isinstance(bc, list)
                assert len(bc) >= 0
                assert bc
                bc1 = batch_geocode(addresses=addresses_dict, source_country='EN', 
                                    category=None, out_sr=None, geocoder=None, 
                                    as_featureset=False, match_out_of_range=True, 
                                    location_type='street', search_extent=None, 
                                    lang_code='EN', preferred_label_values=None)
                assert isinstance(bc1, list)
                assert len(bc1) >= 0
                assert bc1                
                bc2 = batch_geocode(addresses=addresses_dict, source_country='EN', 
                                    category=None, out_sr=4326, geocoder=None, 
                                    as_featureset=False, match_out_of_range=True, 
                                    location_type='street', search_extent=None, 
                                    lang_code='EN', preferred_label_values=None)
                assert isinstance(bc2, list)
                assert len(bc2) >= 0
                assert bc2                
                bc3 = batch_geocode(addresses=addresses_dict, source_country='EN', 
                                    category=None, out_sr=4326, geocoder=None, 
                                    as_featureset=True, match_out_of_range=True, 
                                    location_type='street', search_extent=None, 
                                    lang_code='EN', preferred_label_values=None)
                from arcgis.features import FeatureSet
                assert isinstance(bc3, FeatureSet)
                assert len(bc3) >= 0
                assert bc3                
                bc4 = batch_geocode(addresses=addresses_dict, source_country='EN', 
                                    category=None, out_sr=4326, geocoder=None,
                                    as_featureset=True, match_out_of_range=False, 
                                    location_type='street', search_extent=None, 
                                    lang_code='EN', preferred_label_values=None)
                assert isinstance(bc4, FeatureSet)
                assert len(bc4) >= 0
                assert bc4                
            else:
                gc = None
                l = get_geocoders(gis=gis)
                for gc in get_geocoders(gis=gis):
                    net_loc = urlparse(gis._url.lower()).netloc.lower()
                    if gc.url.lower().find(net_loc) > -1:
                        break
                    else:
                        gc = None
                if gc:
                    bc_ent = batch_geocode(addresses=addresses_dict, source_country=None, category=None, out_sr=None, 
                                           geocoder=gc, as_featureset=False, match_out_of_range=True, location_type='street', 
                                           search_extent=None, lang_code='EN', preferred_label_values=None)
                    assert bc_ent
                    assert len(bc_ent) > 0
    #######################################################################   
    def test_batch_geocode_list(self):
        """tests the batch geocoding operation via list of strings"""
        addresses_dict = ["380 New York St, Redlands, CA",
             "1 World Way, Los Angeles, CA",
             "1200 Getty Center Drive, Los Angeles, CA",
             "5905 Wilshire Boulevard, Los Angeles, CA",
             "100 Universal City Plaza, Universal City, CA 91608",
             "4800 Oak Grove Dr, Pasadena, CA 91109"]
        for p in ['your_enterprise_profile', 'your_online_profile']:
            gis = GIS(profile=p, verify_cert=False)    
            if gis._portal.is_arcgisonline:
                bc = batch_geocode(addresses=addresses_dict, source_country=None, 
                                   category=None, out_sr=None, geocoder=None, 
                                   as_featureset=False, match_out_of_range=True, 
                                   location_type='street', search_extent=None, 
                                   lang_code='EN', preferred_label_values=None)
                assert isinstance(bc, list)
                assert len(bc) >= 5
                assert bc
            else:
                gc = None
                l = get_geocoders(gis=gis)
                for gc in get_geocoders(gis=gis):
                    net_loc = urlparse(gis._url.lower()).netloc.lower()
                    if gc.url.lower().find(net_loc) > -1:
                        break
                    else:
                        gc = None
                if gc:
                    bc_ent = batch_geocode(addresses=addresses_dict, source_country=None, category=None, out_sr=None, 
                                           geocoder=gc, as_featureset=False, match_out_of_range=True, location_type='street', 
                                           search_extent=None, lang_code='EN', preferred_label_values=None)
                    assert bc_ent
                    assert len(bc_ent) > 5
            
    

if __name__ == "__main__":
    unittest.main()