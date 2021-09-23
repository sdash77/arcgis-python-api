from pathlib import Path

try:
    import pandas as pd
except:
    pd = None
from arcgis.features import GeoAccessor, GeoSeriesAccessor


from .agol import gis_agol

csv_pth = Path(__file__).parent.parent / "geoenrich_data" / "seattle_block_group.csv"
block_group_df = pd.read_csv(csv_pth)
block_group_df.spatial.set_geometry("SHAPE")

block_group_points_df = block_group_df.copy()
block_group_points_df.SHAPE = block_group_points_df.SHAPE.apply(
    lambda geom: geom.true_centroid
)
block_group_points_df.spatial.set_geometry("SHAPE")

key_enrich_list_web = [
    "TOTPOP_CY",
    "GQPOP_CY",
    "DIVINDX_CY",
    "TOTHH_CY",
    "AVGHHSZ_CY",
    "MEDHINC_CY",
    "AVGHINC_CY",
    "PCI_CY",
    "TOTHU_CY",
    "OWNER_CY",
    "RENTER_CY",
    "VACANT_CY",
    "MEDVAL_CY",
    "AVGVAL_CY",
    "POPGRW10CY",
    "HHGRW10CY",
    "FAMGRW10CY",
    "DPOP_CY",
    "DPOPWRK_CY",
    "DPOPRES_CY",
]

key_enrich_list_local = [
    "KeyUSFacts.TOTPOP_CY",
    "KeyUSFacts.GQPOP_CY",
    "KeyUSFacts.DIVINDX_CY",
    "KeyUSFacts.TOTHH_CY",
    "KeyUSFacts.AVGHHSZ_CY",
    "KeyUSFacts.MEDHINC_CY",
    "KeyUSFacts.AVGHINC_CY",
    "KeyUSFacts.PCI_CY",
    "KeyUSFacts.TOTHU_CY",
    "KeyUSFacts.OWNER_CY",
    "KeyUSFacts.RENTER_CY",
    "KeyUSFacts.VACANT_CY",
    "KeyUSFacts.MEDVAL_CY",
    "KeyUSFacts.AVGVAL_CY",
    "KeyUSFacts.POPGRW10CY",
    "KeyUSFacts.HHGRW10CY",
    "KeyUSFacts.FAMGRW10CY",
    "KeyUSFacts.DPOP_CY",
    "KeyUSFacts.DPOPWRK_CY",
    "KeyUSFacts.DPOPRES_CY",
]

address_list_str = [
    "777 Brockton Avenue, Abington MA 2351",
    "30 Memorial Drive, Avon MA 2322",
    "250 Hartford Avenue, Bellingham MA 2019",
    "700 Oak Street, Brockton MA 2301",
    "66-4 Parkhurst Rd, Chelmsford MA 1824",
    "591 Memorial Dr, Chicopee MA 1020",
    "55 Brooksby Village Way, Danvers MA 1923",
    "137 Teaticket Hwy, East Falmouth MA 2536",
    "42 Fairhaven Commons Way, Fairhaven MA 2719",
    "374 William S Canning Blvd, Fall River MA 2721",
    "121 Worcester Rd, Framingham MA 1701",
    "677 Timpany Blvd, Gardner MA 1440",
    "337 Russell St, Hadley MA 1035",
    "295 Plymouth Street, Halifax MA 2338",
    "1775 Washington St, Hanover MA 2339",
    "280 Washington Street, Hudson MA 1749",
    "20 Soojian Dr, Leicester MA 1524",
    "11 Jungle Road, Leominster MA 1453",
    "301 Massachusetts Ave, Lunenburg MA 1462",
    "780 Lynnway, Lynn MA 1905",
    "70 Pleasant Valley Street, Methuen MA 1844",
    "830 Curran Memorial Hwy, North Adams MA 1247",
    "1470 S Washington St, North Attleboro MA 2760",
    "506 State Road, North Dartmouth MA 2747",
    "742 Main Street, North Oxford MA 1537",
    "72 Main St, North Reading MA 1864",
    "200 Otis Street, Northborough MA 1532",
    "180 North King Street, Northhampton MA 1060",
    "555 East Main St, Orange MA 1364",
    "555 Hubbard Ave-Suite 12, Pittsfield MA 1201",
    "300 Colony Place, Plymouth MA 2360",
    "301 Falls Blvd, Quincy MA 2169",
    "36 Paramount Drive, Raynham MA 2767",
    "450 Highland Ave, Salem MA 1970",
    "1180 Fall River Avenue, Seekonk MA 2771",
    "1105 Boston Road, Springfield MA 1119",
    "100 Charlton Road, Sturbridge MA 1566",
    "262 Swansea Mall Dr, Swansea MA 2777",
    "333 Main Street, Tewksbury MA 1876",
    "550 Providence Hwy, Walpole MA 2081",
    "352 Palmer Road, Ware MA 1082",
    "3005 Cranberry Hwy Rt 6 28, Wareham MA 2538",
    "250 Rt 59, Airmont NY 10901",
    "141 Washington Ave Extension, Albany NY 12205",
    "13858 Rt 31 W, Albion NY 14411",
    "2055 Niagara Falls Blvd, Amherst NY 14228",
    "101 Sanford Farm Shpg Center, Amsterdam NY 12010",
    "297 Grant Avenue, Auburn NY 13021",
    "4133 Veterans Memorial Drive, Batavia NY 14020",
    "6265 Brockport Spencerport Rd, Brockport NY 14420",
    "5399 W Genesse St, Camillus NY 13031",
    "3191 County rd 10, Canandaigua NY 14424",
    "30 Catskill, Catskill NY 12414",
    "161 Centereach Mall, Centereach NY 11720",
    "3018 East Ave, Central Square NY 13036",
    "100 Thruway Plaza, Cheektowaga NY 14225",
    "8064 Brewerton Rd, Cicero NY 13039",
    "5033 Transit Road, Clarence NY 14031",
    "3949 Route 31, Clay NY 13041",
    "139 Merchant Place, Cobleskill NY 12043",
    "85 Crooked Hill Road, Commack NY 11725",
    "872 Route 13, Cortlandville NY 13045",
    "279 Troy Road, East Greenbush NY 12061",
    "2465 Hempstead Turnpike, East Meadow NY 11554",
    "6438 Basile Rowe, East Syracuse NY 13057",
    "25737 US Rt 11, Evans Mills NY 13637",
    "901 Route 110, Farmingdale NY 11735",
    "2400 Route 9, Fishkill NY 12524",
    "10401 Bennett Road, Fredonia NY 14063",
    "1818 State Route 3, Fulton NY 13069",
    "4300 Lakeville Road, Geneseo NY 14454",
    "990 Route 5 20, Geneva NY 14456",
    "311 RT 9W, Glenmont NY 12077",
    "200 Dutch Meadows Ln, Glenville NY 12302",
    "100 Elm Ridge Center Dr, Greece NY 14626",
    "1549 Rt 9, Halfmoon NY 12065",
    "5360 Southwestern Blvd, Hamburg NY 14075",
    "103 North Caroline St, Herkimer NY 13350",
    "1000 State Route 36, Hornell NY 14843",
    "1400 County Rd 64, Horseheads NY 14845",
    "135 Fairgrounds Memorial Pkwy, Ithaca NY 14850",
    "2 Gannett Dr, Johnson City NY 13790",
    "233 5th Ave Ext, Johnstown NY 12095",
    "601 Frank Stottile Blvd, Kingston NY 12401",
    "350 E Fairmount Ave, Lakewood NY 14750",
    "4975 Transit Rd, Lancaster NY 14086",
    "579 Troy-Schenectady Road, Latham NY 12110",
    "5783 So Transit Road, Lockport NY 14094",
    "7155 State Rt 12 S, Lowville NY 13367",
    "425 Route 31, Macedon NY 14502",
    "3222 State Rt 11, Malone NY 12953",
    "200 Sunrise Mall, Massapequa NY 11758",
    "43 Stephenville St, Massena NY 13662",
    "750 Middle Country Road, Middle Island NY 11953",
    "470 Route 211 East, Middletown NY 10940",
    "3133 E Main St, Mohegan Lake NY 10547",
    "288 Larkin, Monroe NY 10950",
    "41 Anawana Lake Road, Monticello NY 12701",
    "4765 Commercial Drive, New Hartford NY 13413",
    "1201 Rt 300, Newburgh NY 12550",
    "255 W Main St, Avon CT 6001",
    "120 Commercial Parkway, Branford CT 6405",
    "1400 Farmington Ave, Bristol CT 6010",
    "161 Berlin Road, Cromwell CT 6416",
    "67 Newton Rd, Danbury CT 6810",
    "656 New Haven Ave, Derby CT 6418",
    "69 Prospect Hill Road, East Windsor CT 6088",
    "150 Gold Star Hwy, Groton CT 6340",
    "900 Boston Post Road, Guilford CT 6437",
    "2300 Dixwell Ave, Hamden CT 6514",
    "495 Flatbush Ave, Hartford CT 6106",
    "180 River Rd, Lisbon CT 6351",
    "420 Buckland Hills Dr, Manchester CT 6040",
    "1365 Boston Post Road, Milford CT 6460",
    "1100 New Haven Road, Naugatuck CT 6770",
    "315 Foxon Blvd, New Haven CT 6513",
    "164 Danbury Rd, New Milford CT 6776",
    "3164 Berlin Turnpike, Newington CT 6111",
    "474 Boston Post Road, North Windham CT 6256",
    "650 Main Ave, Norwalk CT 6851",
    "680 Connecticut Avenue, Norwalk CT 6854",
    "220 Salem Turnpike, Norwich CT 6360",
    "655 Boston Post Rd, Old Saybrook CT 6475",
    "625 School Street, Putnam CT 6260",
    "80 Town Line Rd, Rocky Hill CT 6067",
    "465 Bridgeport Avenue, Shelton CT 6484",
    "235 Queen St, Southington CT 6489",
    "150 Barnum Avenue Cutoff, Stratford CT 6614",
    "970 Torringford Street, Torrington CT 6790",
    "844 No Colony Road, Wallingford CT 6492",
    "910 Wolcott St, Waterbury CT 6705",
    "155 Waterford Parkway No, Waterford CT 6385",
    "515 Sawmill Road, West Haven CT 6516",
    "2473 Hackworth Road, Adamsville AL 35005",
    "630 Coonial Promenade Pkwy, Alabaster AL 35007",
    "2643 Hwy 280 West, Alexander City AL 35010",
    "540 West Bypass, Andalusia AL 36420",
    "5560 Mcclellan Blvd, Anniston AL 36206",
    "1450 No Brindlee Mtn Pkwy, Arab AL 35016",
    "1011 US Hwy 72 East, Athens AL 35611",
    "973 Gilbert Ferry Road Se, Attalla AL 35954",
    "1717 South College Street, Auburn AL 36830",
    "701 Mcmeans Ave, Bay Minette AL 36507",
    "750 Academy Drive, Bessemer AL 35022",
    "312 Palisades Blvd, Birmingham AL 35209",
    "1600 Montclair Rd, Birmingham AL 35210",
    "5919 Trussville Crossings Pkwy, Birmingham AL 35235",
    "9248 Parkway East, Birmingham AL 35206",
    "1972 Hwy 431, Boaz AL 35957",
    "10675 Hwy 5, Brent AL 35034",
    "2041 Douglas Avenue, Brewton AL 36426",
    "5100 Hwy 31, Calera AL 35040",
    "1916 Center Point Rd, Center Point AL 35215",
    "1950 W Main St, Centre AL 35960",
    "16077 Highway 280, Chelsea AL 35043",
    "1415 7Th Street South, Clanton AL 35045",
    "626 Olive Street Sw, Cullman AL 35055",
    "27520 Hwy 98, Daphne AL 36526",
    "2800 Spring Avn SW, Decatur AL 35603",
    "969 Us Hwy 80 West, Demopolis AL 36732",
    "3300 South Oates Street, Dothan AL 36301",
    "4310 Montgomery Hwy, Dothan AL 36303",
    "600 Boll Weevil Circle, Enterprise AL 36330",
    "3176 South Eufaula Avenue, Eufaula AL 36027",
    "7100 Aaron Aronov Drive, Fairfield AL 35064",
    "10040 County Road 48, Fairhope AL 36533",
    "3186 Hwy 171 North, Fayette AL 35555",
    "3100 Hough Rd, Florence AL 35630",
    "2200 South Mckenzie St, Foley AL 36535",
    "2001 Glenn Bldv Sw, Fort Payne AL 35968",
    "340 East Meighan Blvd, Gadsden AL 35903",
    "890 Odum Road, Gardendale AL 35071",
    "1608 W Magnolia Ave, Geneva AL 36340",
    "501 Willow Lane, Greenville AL 36037",
    "170 Fort Morgan Road, Gulf Shores AL 36542",
    "11697 US Hwy 431, Guntersville AL 35976",
    "42417 Hwy 195, Haleyville AL 35565",
    "1706 Military Street South, Hamilton AL 35570",
    "1201 Hwy 31 NW, Hartselle AL 35640",
    "209 Lakeshore Parkway, Homewood AL 35209",
    "2780 John Hawkins Pkwy, Hoover AL 35244",
    "5335 Hwy 280 South, Hoover AL 35242",
    "1007 Red Farmer Drive, Hueytown AL 35023",
    "2900 S Mem PkwyDrake Ave, Huntsville AL 35801",
    "11610 Memorial Pkwy South, Huntsville AL 35803",
    "2200 Sparkman Drive, Huntsville AL 35810",
    "330 Sutton Rd, Huntsville AL 35763",
    "6140A Univ Drive, Huntsville AL 35806",
    "4206 N College Ave, Jackson AL 36545",
    "1625 Pelham South, Jacksonville AL 36265",
    "1801 Hwy 78 East, Jasper AL 35501",
    "8551 Whitfield Ave, Leeds AL 35094",
    "8650 Madison Blvd, Madison AL 35758",
    "145 Kelley Blvd, Millbrook AL 36054",
    "1970 S University Blvd, Mobile AL 36609",
    "6350 Cottage Hill Road, Mobile AL 36609",
    "101 South Beltline Highway, Mobile AL 36606",
    "2500 Dawes Road, Mobile AL 36695",
    "5245 Rangeline Service Rd, Mobile AL 36619",
    "685 Schillinger Rd, Mobile AL 36695",
    "3371 S Alabama Ave, Monroeville AL 36460",
    "10710 Chantilly Pkwy, Montgomery AL 36117",
    "3801 Eastern Blvd, Montgomery AL 36116",
    "6495 Atlanta Hwy, Montgomery AL 36117",
    "851 Ann St, Montgomery AL 36107",
    "15445 Highway 24, Moulton AL 35650",
    "517 West Avalon Ave, Muscle Shoals AL 35661",
    "5710 Mcfarland Blvd, Northport AL 35476",
    "2453 2Nd Avenue East, Oneonta AL 35121  205-625-647",
    "2900 Pepperrell Pkwy, Opelika AL 36801",
    "92 Plaza Lane, Oxford AL 36203",
    "1537 Hwy 231 South, Ozark AL 36360",
    "2181 Pelham Pkwy, Pelham AL 35124",
    "165 Vaughan Ln, Pell City AL 35125",
    "3700 Hwy 280-431 N, Phenix City AL 36867",
    "1903 Cobbs Ford Rd, Prattville AL 36066",
    "4180 Us Hwy 431, Roanoke AL 36274",
    "13675 Hwy 43, Russellville AL 35653",
    "1095 Industrial Pkwy, Saraland AL 36571",
    "24833 Johnt Reidprkw, Scottsboro AL 35768",
    "1501 Hwy 14 East, Selma AL 36703",
    "7855 Moffett Rd, Semmes AL 36575",
    "150 Springville Station Blvd, Springville AL 35146",
    "690 Hwy 78, Sumiton AL 35148",
    "41301 US Hwy 280, Sylacauga AL 35150",
    "214 Haynes Street, Talladega AL 35160",
    "1300 Gilmer Ave, Tallassee AL 36078",
    "34301 Hwy 43, Thomasville AL 36784",
    "1420 Us 231 South, Troy AL 36081",
    "1501 Skyland Blvd E, Tuscaloosa AL 35405",
    "3501 20th Av, Valley AL 36854",
    "1300 Montgomery Highway, Vestavia Hills AL 35216",
    "4538 Us Hwy 231, Wetumpka AL 36092",
    "2575 Us Hwy 43, Winfield AL 35594",
]

address_list_json = [
    {
        "address": {
            "Address": "777 Brockton Avenue",
            "Admin1": "Abington",
            "Admin2": "MA",
            "Postal": "02351",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "30 Memorial Drive",
            "Admin1": "Avon",
            "Admin2": "MA",
            "Postal": "02322",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "250 Hartford Avenue",
            "Admin1": "Bellingham",
            "Admin2": "MA",
            "Postal": "02019",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "700 Oak Street",
            "Admin1": "Brockton",
            "Admin2": "MA",
            "Postal": "02301",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "66-4 Parkhurst Rd",
            "Admin1": "Chelmsford",
            "Admin2": "MA",
            "Postal": "01824",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "591 Memorial Dr",
            "Admin1": "Chicopee",
            "Admin2": "MA",
            "Postal": "01020",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "55 Brooksby Village Way",
            "Admin1": "Danvers",
            "Admin2": "MA",
            "Postal": "01923",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "137 Teaticket Hwy",
            "Admin1": "East Falmouth",
            "Admin2": "MA",
            "Postal": "02536",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "42 Fairhaven Commons Way",
            "Admin1": "Fairhaven",
            "Admin2": "MA",
            "Postal": "02719",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "374 William S Canning Blvd",
            "Admin1": "Fall River",
            "Admin2": "MA",
            "Postal": "02721",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "121 Worcester Rd",
            "Admin1": "Framingham",
            "Admin2": "MA",
            "Postal": "01701",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "677 Timpany Blvd",
            "Admin1": "Gardner",
            "Admin2": "MA",
            "Postal": "01440",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "337 Russell St",
            "Admin1": "Hadley",
            "Admin2": "MA",
            "Postal": "01035",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "295 Plymouth Street",
            "Admin1": "Halifax",
            "Admin2": "MA",
            "Postal": "02338",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1775 Washington St",
            "Admin1": "Hanover",
            "Admin2": "MA",
            "Postal": "02339",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "280 Washington Street",
            "Admin1": "Hudson",
            "Admin2": "MA",
            "Postal": "01749",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "20 Soojian Dr",
            "Admin1": "Leicester",
            "Admin2": "MA",
            "Postal": "01524",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "11 Jungle Road",
            "Admin1": "Leominster",
            "Admin2": "MA",
            "Postal": "01453",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "301 Massachusetts Ave",
            "Admin1": "Lunenburg",
            "Admin2": "MA",
            "Postal": "01462",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "780 Lynnway",
            "Admin1": "Lynn",
            "Admin2": "MA",
            "Postal": "01905",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "70 Pleasant Valley Street",
            "Admin1": "Methuen",
            "Admin2": "MA",
            "Postal": "01844",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "830 Curran Memorial Hwy",
            "Admin1": "North Adams",
            "Admin2": "MA",
            "Postal": "01247",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1470 S Washington St",
            "Admin1": "North Attleboro",
            "Admin2": "MA",
            "Postal": "02760",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "506 State Road",
            "Admin1": "North Dartmouth",
            "Admin2": "MA",
            "Postal": "02747",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "742 Main Street",
            "Admin1": "North Oxford",
            "Admin2": "MA",
            "Postal": "01537",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "72 Main St",
            "Admin1": "North Reading",
            "Admin2": "MA",
            "Postal": "01864",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "200 Otis Street",
            "Admin1": "Northborough",
            "Admin2": "MA",
            "Postal": "01532",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "180 North King Street",
            "Admin1": "Northhampton",
            "Admin2": "MA",
            "Postal": "01060",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "555 East Main St",
            "Admin1": "Orange",
            "Admin2": "MA",
            "Postal": "01364",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "555 Hubbard Ave-Suite 12",
            "Admin1": "Pittsfield",
            "Admin2": "MA",
            "Postal": "01201",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "300 Colony Place",
            "Admin1": "Plymouth",
            "Admin2": "MA",
            "Postal": "02360",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "301 Falls Blvd",
            "Admin1": "Quincy",
            "Admin2": "MA",
            "Postal": "02169",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "36 Paramount Drive",
            "Admin1": "Raynham",
            "Admin2": "MA",
            "Postal": "02767",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "450 Highland Ave",
            "Admin1": "Salem",
            "Admin2": "MA",
            "Postal": "01970",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1180 Fall River Avenue",
            "Admin1": "Seekonk",
            "Admin2": "MA",
            "Postal": "02771",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1105 Boston Road",
            "Admin1": "Springfield",
            "Admin2": "MA",
            "Postal": "01119",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "100 Charlton Road",
            "Admin1": "Sturbridge",
            "Admin2": "MA",
            "Postal": "01566",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "262 Swansea Mall Dr",
            "Admin1": "Swansea",
            "Admin2": "MA",
            "Postal": "02777",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "333 Main Street",
            "Admin1": "Tewksbury",
            "Admin2": "MA",
            "Postal": "01876",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "550 Providence Hwy",
            "Admin1": "Walpole",
            "Admin2": "MA",
            "Postal": "02081",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "352 Palmer Road",
            "Admin1": "Ware",
            "Admin2": "MA",
            "Postal": "01082",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "3005 Cranberry Hwy Rt 6 28",
            "Admin1": "Wareham",
            "Admin2": "MA",
            "Postal": "02538",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "250 Rt 59",
            "Admin1": "Airmont",
            "Admin2": "NY",
            "Postal": "10901",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "141 Washington Ave Extension",
            "Admin1": "Albany",
            "Admin2": "NY",
            "Postal": "12205",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "13858 Rt 31 W",
            "Admin1": "Albion",
            "Admin2": "NY",
            "Postal": "14411",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "2055 Niagara Falls Blvd",
            "Admin1": "Amherst",
            "Admin2": "NY",
            "Postal": "14228",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "101 Sanford Farm Shpg Center",
            "Admin1": "Amsterdam",
            "Admin2": "NY",
            "Postal": "12010",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "297 Grant Avenue",
            "Admin1": "Auburn",
            "Admin2": "NY",
            "Postal": "13021",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "4133 Veterans Memorial Drive",
            "Admin1": "Batavia",
            "Admin2": "NY",
            "Postal": "14020",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "6265 Brockport Spencerport Rd",
            "Admin1": "Brockport",
            "Admin2": "NY",
            "Postal": "14420",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "5399 W Genesse St",
            "Admin1": "Camillus",
            "Admin2": "NY",
            "Postal": "13031",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "3191 County rd 10",
            "Admin1": "Canandaigua",
            "Admin2": "NY",
            "Postal": "14424",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "30 Catskill",
            "Admin1": "Catskill",
            "Admin2": "NY",
            "Postal": "12414",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "161 Centereach Mall",
            "Admin1": "Centereach",
            "Admin2": "NY",
            "Postal": "11720",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "3018 East Ave",
            "Admin1": "Central Square",
            "Admin2": "NY",
            "Postal": "13036",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "100 Thruway Plaza",
            "Admin1": "Cheektowaga",
            "Admin2": "NY",
            "Postal": "14225",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "8064 Brewerton Rd",
            "Admin1": "Cicero",
            "Admin2": "NY",
            "Postal": "13039",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "5033 Transit Road",
            "Admin1": "Clarence",
            "Admin2": "NY",
            "Postal": "14031",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "3949 Route 31",
            "Admin1": "Clay",
            "Admin2": "NY",
            "Postal": "13041",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "139 Merchant Place",
            "Admin1": "Cobleskill",
            "Admin2": "NY",
            "Postal": "12043",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "85 Crooked Hill Road",
            "Admin1": "Commack",
            "Admin2": "NY",
            "Postal": "11725",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "872 Route 13",
            "Admin1": "Cortlandville",
            "Admin2": "NY",
            "Postal": "13045",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "279 Troy Road",
            "Admin1": "East Greenbush",
            "Admin2": "NY",
            "Postal": "12061",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "2465 Hempstead Turnpike",
            "Admin1": "East Meadow",
            "Admin2": "NY",
            "Postal": "11554",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "6438 Basile Rowe",
            "Admin1": "East Syracuse",
            "Admin2": "NY",
            "Postal": "13057",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "25737 US Rt 11",
            "Admin1": "Evans Mills",
            "Admin2": "NY",
            "Postal": "13637",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "901 Route 110",
            "Admin1": "Farmingdale",
            "Admin2": "NY",
            "Postal": "11735",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "2400 Route 9",
            "Admin1": "Fishkill",
            "Admin2": "NY",
            "Postal": "12524",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "10401 Bennett Road",
            "Admin1": "Fredonia",
            "Admin2": "NY",
            "Postal": "14063",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1818 State Route 3",
            "Admin1": "Fulton",
            "Admin2": "NY",
            "Postal": "13069",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "4300 Lakeville Road",
            "Admin1": "Geneseo",
            "Admin2": "NY",
            "Postal": "14454",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "990 Route 5 20",
            "Admin1": "Geneva",
            "Admin2": "NY",
            "Postal": "14456",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "311 RT 9W",
            "Admin1": "Glenmont",
            "Admin2": "NY",
            "Postal": "12077",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "200 Dutch Meadows Ln",
            "Admin1": "Glenville",
            "Admin2": "NY",
            "Postal": "12302",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "100 Elm Ridge Center Dr",
            "Admin1": "Greece",
            "Admin2": "NY",
            "Postal": "14626",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1549 Rt 9",
            "Admin1": "Halfmoon",
            "Admin2": "NY",
            "Postal": "12065",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "5360 Southwestern Blvd",
            "Admin1": "Hamburg",
            "Admin2": "NY",
            "Postal": "14075",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "103 North Caroline St",
            "Admin1": "Herkimer",
            "Admin2": "NY",
            "Postal": "13350",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1000 State Route 36",
            "Admin1": "Hornell",
            "Admin2": "NY",
            "Postal": "14843",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1400 County Rd 64",
            "Admin1": "Horseheads",
            "Admin2": "NY",
            "Postal": "14845",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "135 Fairgrounds Memorial Pkwy",
            "Admin1": "Ithaca",
            "Admin2": "NY",
            "Postal": "14850",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "2 Gannett Dr",
            "Admin1": "Johnson City",
            "Admin2": "NY",
            "Postal": "13790",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "233 5th Ave Ext",
            "Admin1": "Johnstown",
            "Admin2": "NY",
            "Postal": "12095",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "601 Frank Stottile Blvd",
            "Admin1": "Kingston",
            "Admin2": "NY",
            "Postal": "12401",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "350 E Fairmount Ave",
            "Admin1": "Lakewood",
            "Admin2": "NY",
            "Postal": "14750",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "4975 Transit Rd",
            "Admin1": "Lancaster",
            "Admin2": "NY",
            "Postal": "14086",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "579 Troy-Schenectady Road",
            "Admin1": "Latham",
            "Admin2": "NY",
            "Postal": "12110",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "5783 So Transit Road",
            "Admin1": "Lockport",
            "Admin2": "NY",
            "Postal": "14094",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "7155 State Rt 12 S",
            "Admin1": "Lowville",
            "Admin2": "NY",
            "Postal": "13367",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "425 Route 31",
            "Admin1": "Macedon",
            "Admin2": "NY",
            "Postal": "14502",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "3222 State Rt 11",
            "Admin1": "Malone",
            "Admin2": "NY",
            "Postal": "12953",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "200 Sunrise Mall",
            "Admin1": "Massapequa",
            "Admin2": "NY",
            "Postal": "11758",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "43 Stephenville St",
            "Admin1": "Massena",
            "Admin2": "NY",
            "Postal": "13662",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "750 Middle Country Road",
            "Admin1": "Middle Island",
            "Admin2": "NY",
            "Postal": "11953",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "470 Route 211 East",
            "Admin1": "Middletown",
            "Admin2": "NY",
            "Postal": "10940",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "3133 E Main St",
            "Admin1": "Mohegan Lake",
            "Admin2": "NY",
            "Postal": "10547",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "288 Larkin",
            "Admin1": "Monroe",
            "Admin2": "NY",
            "Postal": "10950",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "41 Anawana Lake Road",
            "Admin1": "Monticello",
            "Admin2": "NY",
            "Postal": "12701",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "4765 Commercial Drive",
            "Admin1": "New Hartford",
            "Admin2": "NY",
            "Postal": "13413",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1201 Rt 300",
            "Admin1": "Newburgh",
            "Admin2": "NY",
            "Postal": "12550",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "255 W Main St",
            "Admin1": "Avon",
            "Admin2": "CT",
            "Postal": "06001",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "120 Commercial Parkway",
            "Admin1": "Branford",
            "Admin2": "CT",
            "Postal": "06405",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1400 Farmington Ave",
            "Admin1": "Bristol",
            "Admin2": "CT",
            "Postal": "06010",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "161 Berlin Road",
            "Admin1": "Cromwell",
            "Admin2": "CT",
            "Postal": "06416",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "67 Newton Rd",
            "Admin1": "Danbury",
            "Admin2": "CT",
            "Postal": "06810",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "656 New Haven Ave",
            "Admin1": "Derby",
            "Admin2": "CT",
            "Postal": "06418",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "69 Prospect Hill Road",
            "Admin1": "East Windsor",
            "Admin2": "CT",
            "Postal": "06088",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "150 Gold Star Hwy",
            "Admin1": "Groton",
            "Admin2": "CT",
            "Postal": "06340",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "900 Boston Post Road",
            "Admin1": "Guilford",
            "Admin2": "CT",
            "Postal": "06437",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "2300 Dixwell Ave",
            "Admin1": "Hamden",
            "Admin2": "CT",
            "Postal": "06514",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "495 Flatbush Ave",
            "Admin1": "Hartford",
            "Admin2": "CT",
            "Postal": "06106",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "180 River Rd",
            "Admin1": "Lisbon",
            "Admin2": "CT",
            "Postal": "06351",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "420 Buckland Hills Dr",
            "Admin1": "Manchester",
            "Admin2": "CT",
            "Postal": "06040",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1365 Boston Post Road",
            "Admin1": "Milford",
            "Admin2": "CT",
            "Postal": "06460",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1100 New Haven Road",
            "Admin1": "Naugatuck",
            "Admin2": "CT",
            "Postal": "06770",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "315 Foxon Blvd",
            "Admin1": "New Haven",
            "Admin2": "CT",
            "Postal": "06513",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "164 Danbury Rd",
            "Admin1": "New Milford",
            "Admin2": "CT",
            "Postal": "06776",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "3164 Berlin Turnpike",
            "Admin1": "Newington",
            "Admin2": "CT",
            "Postal": "06111",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "474 Boston Post Road",
            "Admin1": "North Windham",
            "Admin2": "CT",
            "Postal": "06256",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "650 Main Ave",
            "Admin1": "Norwalk",
            "Admin2": "CT",
            "Postal": "06851",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "680 Connecticut Avenue",
            "Admin1": "Norwalk",
            "Admin2": "CT",
            "Postal": "06854",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "220 Salem Turnpike",
            "Admin1": "Norwich",
            "Admin2": "CT",
            "Postal": "06360",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "655 Boston Post Rd",
            "Admin1": "Old Saybrook",
            "Admin2": "CT",
            "Postal": "06475",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "625 School Street",
            "Admin1": "Putnam",
            "Admin2": "CT",
            "Postal": "06260",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "80 Town Line Rd",
            "Admin1": "Rocky Hill",
            "Admin2": "CT",
            "Postal": "06067",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "465 Bridgeport Avenue",
            "Admin1": "Shelton",
            "Admin2": "CT",
            "Postal": "06484",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "235 Queen St",
            "Admin1": "Southington",
            "Admin2": "CT",
            "Postal": "06489",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "150 Barnum Avenue Cutoff",
            "Admin1": "Stratford",
            "Admin2": "CT",
            "Postal": "06614",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "970 Torringford Street",
            "Admin1": "Torrington",
            "Admin2": "CT",
            "Postal": "06790",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "844 No Colony Road",
            "Admin1": "Wallingford",
            "Admin2": "CT",
            "Postal": "06492",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "910 Wolcott St",
            "Admin1": "Waterbury",
            "Admin2": "CT",
            "Postal": "06705",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "155 Waterford Parkway No",
            "Admin1": "Waterford",
            "Admin2": "CT",
            "Postal": "06385",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "515 Sawmill Road",
            "Admin1": "West Haven",
            "Admin2": "CT",
            "Postal": "06516",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "2473 Hackworth Road",
            "Admin1": "Adamsville",
            "Admin2": "AL",
            "Postal": "35005",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "630 Coonial Promenade Pkwy",
            "Admin1": "Alabaster",
            "Admin2": "AL",
            "Postal": "35007",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "2643 Hwy 280 West",
            "Admin1": "Alexander City",
            "Admin2": "AL",
            "Postal": "35010",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "540 West Bypass",
            "Admin1": "Andalusia",
            "Admin2": "AL",
            "Postal": "36420",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "5560 Mcclellan Blvd",
            "Admin1": "Anniston",
            "Admin2": "AL",
            "Postal": "36206",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1450 No Brindlee Mtn Pkwy",
            "Admin1": "Arab",
            "Admin2": "AL",
            "Postal": "35016",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1011 US Hwy 72 East",
            "Admin1": "Athens",
            "Admin2": "AL",
            "Postal": "35611",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "973 Gilbert Ferry Road Se",
            "Admin1": "Attalla",
            "Admin2": "AL",
            "Postal": "35954",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1717 South College Street",
            "Admin1": "Auburn",
            "Admin2": "AL",
            "Postal": "36830",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "701 Mcmeans Ave",
            "Admin1": "Bay Minette",
            "Admin2": "AL",
            "Postal": "36507",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "750 Academy Drive",
            "Admin1": "Bessemer",
            "Admin2": "AL",
            "Postal": "35022",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "312 Palisades Blvd",
            "Admin1": "Birmingham",
            "Admin2": "AL",
            "Postal": "35209",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1600 Montclair Rd",
            "Admin1": "Birmingham",
            "Admin2": "AL",
            "Postal": "35210",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "5919 Trussville Crossings Pkwy",
            "Admin1": "Birmingham",
            "Admin2": "AL",
            "Postal": "35235",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "9248 Parkway East",
            "Admin1": "Birmingham",
            "Admin2": "AL",
            "Postal": "35206",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1972 Hwy 431",
            "Admin1": "Boaz",
            "Admin2": "AL",
            "Postal": "35957",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "10675 Hwy 5",
            "Admin1": "Brent",
            "Admin2": "AL",
            "Postal": "35034",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "2041 Douglas Avenue",
            "Admin1": "Brewton",
            "Admin2": "AL",
            "Postal": "36426",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "5100 Hwy 31",
            "Admin1": "Calera",
            "Admin2": "AL",
            "Postal": "35040",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1916 Center Point Rd",
            "Admin1": "Center Point",
            "Admin2": "AL",
            "Postal": "35215",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1950 W Main St",
            "Admin1": "Centre",
            "Admin2": "AL",
            "Postal": "35960",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "16077 Highway 280",
            "Admin1": "Chelsea",
            "Admin2": "AL",
            "Postal": "35043",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1415 7Th Street South",
            "Admin1": "Clanton",
            "Admin2": "AL",
            "Postal": "35045",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "626 Olive Street Sw",
            "Admin1": "Cullman",
            "Admin2": "AL",
            "Postal": "35055",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "27520 Hwy 98",
            "Admin1": "Daphne",
            "Admin2": "AL",
            "Postal": "36526",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "2800 Spring Avn SW",
            "Admin1": "Decatur",
            "Admin2": "AL",
            "Postal": "35603",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "969 Us Hwy 80 West",
            "Admin1": "Demopolis",
            "Admin2": "AL",
            "Postal": "36732",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "3300 South Oates Street",
            "Admin1": "Dothan",
            "Admin2": "AL",
            "Postal": "36301",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "4310 Montgomery Hwy",
            "Admin1": "Dothan",
            "Admin2": "AL",
            "Postal": "36303",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "600 Boll Weevil Circle",
            "Admin1": "Enterprise",
            "Admin2": "AL",
            "Postal": "36330",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "3176 South Eufaula Avenue",
            "Admin1": "Eufaula",
            "Admin2": "AL",
            "Postal": "36027",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "7100 Aaron Aronov Drive",
            "Admin1": "Fairfield",
            "Admin2": "AL",
            "Postal": "35064",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "10040 County Road 48",
            "Admin1": "Fairhope",
            "Admin2": "AL",
            "Postal": "36533",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "3186 Hwy 171 North",
            "Admin1": "Fayette",
            "Admin2": "AL",
            "Postal": "35555",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "3100 Hough Rd",
            "Admin1": "Florence",
            "Admin2": "AL",
            "Postal": "35630",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "2200 South Mckenzie St",
            "Admin1": "Foley",
            "Admin2": "AL",
            "Postal": "36535",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "2001 Glenn Bldv Sw",
            "Admin1": "Fort Payne",
            "Admin2": "AL",
            "Postal": "35968",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "340 East Meighan Blvd",
            "Admin1": "Gadsden",
            "Admin2": "AL",
            "Postal": "35903",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "890 Odum Road",
            "Admin1": "Gardendale",
            "Admin2": "AL",
            "Postal": "35071",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1608 W Magnolia Ave",
            "Admin1": "Geneva",
            "Admin2": "AL",
            "Postal": "36340",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "501 Willow Lane",
            "Admin1": "Greenville",
            "Admin2": "AL",
            "Postal": "36037",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "170 Fort Morgan Road",
            "Admin1": "Gulf Shores",
            "Admin2": "AL",
            "Postal": "36542",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "11697 US Hwy 431",
            "Admin1": "Guntersville",
            "Admin2": "AL",
            "Postal": "35976",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "42417 Hwy 195",
            "Admin1": "Haleyville",
            "Admin2": "AL",
            "Postal": "35565",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1706 Military Street South",
            "Admin1": "Hamilton",
            "Admin2": "AL",
            "Postal": "35570",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1201 Hwy 31 NW",
            "Admin1": "Hartselle",
            "Admin2": "AL",
            "Postal": "35640",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "209 Lakeshore Parkway",
            "Admin1": "Homewood",
            "Admin2": "AL",
            "Postal": "35209",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "2780 John Hawkins Pkwy",
            "Admin1": "Hoover",
            "Admin2": "AL",
            "Postal": "35244",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "5335 Hwy 280 South",
            "Admin1": "Hoover",
            "Admin2": "AL",
            "Postal": "35242",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1007 Red Farmer Drive",
            "Admin1": "Hueytown",
            "Admin2": "AL",
            "Postal": "35023",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "2900 S Mem PkwyDrake Ave",
            "Admin1": "Huntsville",
            "Admin2": "AL",
            "Postal": "35801",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "11610 Memorial Pkwy South",
            "Admin1": "Huntsville",
            "Admin2": "AL",
            "Postal": "35803",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "2200 Sparkman Drive",
            "Admin1": "Huntsville",
            "Admin2": "AL",
            "Postal": "35810",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "330 Sutton Rd",
            "Admin1": "Huntsville",
            "Admin2": "AL",
            "Postal": "35763",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "6140A Univ Drive",
            "Admin1": "Huntsville",
            "Admin2": "AL",
            "Postal": "35806",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "4206 N College Ave",
            "Admin1": "Jackson",
            "Admin2": "AL",
            "Postal": "36545",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1625 Pelham South",
            "Admin1": "Jacksonville",
            "Admin2": "AL",
            "Postal": "36265",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1801 Hwy 78 East",
            "Admin1": "Jasper",
            "Admin2": "AL",
            "Postal": "35501",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "8551 Whitfield Ave",
            "Admin1": "Leeds",
            "Admin2": "AL",
            "Postal": "35094",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "8650 Madison Blvd",
            "Admin1": "Madison",
            "Admin2": "AL",
            "Postal": "35758",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "145 Kelley Blvd",
            "Admin1": "Millbrook",
            "Admin2": "AL",
            "Postal": "36054",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1970 S University Blvd",
            "Admin1": "Mobile",
            "Admin2": "AL",
            "Postal": "36609",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "6350 Cottage Hill Road",
            "Admin1": "Mobile",
            "Admin2": "AL",
            "Postal": "36609",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "101 South Beltline Highway",
            "Admin1": "Mobile",
            "Admin2": "AL",
            "Postal": "36606",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "2500 Dawes Road",
            "Admin1": "Mobile",
            "Admin2": "AL",
            "Postal": "36695",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "5245 Rangeline Service Rd",
            "Admin1": "Mobile",
            "Admin2": "AL",
            "Postal": "36619",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "685 Schillinger Rd",
            "Admin1": "Mobile",
            "Admin2": "AL",
            "Postal": "36695",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "3371 S Alabama Ave",
            "Admin1": "Monroeville",
            "Admin2": "AL",
            "Postal": "36460",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "10710 Chantilly Pkwy",
            "Admin1": "Montgomery",
            "Admin2": "AL",
            "Postal": "36117",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "3801 Eastern Blvd",
            "Admin1": "Montgomery",
            "Admin2": "AL",
            "Postal": "36116",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "6495 Atlanta Hwy",
            "Admin1": "Montgomery",
            "Admin2": "AL",
            "Postal": "36117",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "851 Ann St",
            "Admin1": "Montgomery",
            "Admin2": "AL",
            "Postal": "36107",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "15445 Highway 24",
            "Admin1": "Moulton",
            "Admin2": "AL",
            "Postal": "35650",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "517 West Avalon Ave",
            "Admin1": "Muscle Shoals",
            "Admin2": "AL",
            "Postal": "35661",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "5710 Mcfarland Blvd",
            "Admin1": "Northport",
            "Admin2": "AL",
            "Postal": "35476",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "2453 2Nd Avenue East",
            "Admin1": "Oneonta",
            "Admin2": "AL",
            "Postal": "35121",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "2900 Pepperrell Pkwy",
            "Admin1": "Opelika",
            "Admin2": "AL",
            "Postal": "36801",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "92 Plaza Lane",
            "Admin1": "Oxford",
            "Admin2": "AL",
            "Postal": "36203",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1537 Hwy 231 South",
            "Admin1": "Ozark",
            "Admin2": "AL",
            "Postal": "36360",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "2181 Pelham Pkwy",
            "Admin1": "Pelham",
            "Admin2": "AL",
            "Postal": "35124",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "165 Vaughan Ln",
            "Admin1": "Pell City",
            "Admin2": "AL",
            "Postal": "35125",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "3700 Hwy 280-431 N",
            "Admin1": "Phenix City",
            "Admin2": "AL",
            "Postal": "36867",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1903 Cobbs Ford Rd",
            "Admin1": "Prattville",
            "Admin2": "AL",
            "Postal": "36066",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "4180 Us Hwy 431",
            "Admin1": "Roanoke",
            "Admin2": "AL",
            "Postal": "36274",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "13675 Hwy 43",
            "Admin1": "Russellville",
            "Admin2": "AL",
            "Postal": "35653",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1095 Industrial Pkwy",
            "Admin1": "Saraland",
            "Admin2": "AL",
            "Postal": "36571",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "24833 Johnt Reidprkw",
            "Admin1": "Scottsboro",
            "Admin2": "AL",
            "Postal": "35768",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1501 Hwy 14 East",
            "Admin1": "Selma",
            "Admin2": "AL",
            "Postal": "36703",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "7855 Moffett Rd",
            "Admin1": "Semmes",
            "Admin2": "AL",
            "Postal": "36575",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "150 Springville Station Blvd",
            "Admin1": "Springville",
            "Admin2": "AL",
            "Postal": "35146",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "690 Hwy 78",
            "Admin1": "Sumiton",
            "Admin2": "AL",
            "Postal": "35148",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "41301 US Hwy 280",
            "Admin1": "Sylacauga",
            "Admin2": "AL",
            "Postal": "35150",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "214 Haynes Street",
            "Admin1": "Talladega",
            "Admin2": "AL",
            "Postal": "35160",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1300 Gilmer Ave",
            "Admin1": "Tallassee",
            "Admin2": "AL",
            "Postal": "36078",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "34301 Hwy 43",
            "Admin1": "Thomasville",
            "Admin2": "AL",
            "Postal": "36784",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1420 Us 231 South",
            "Admin1": "Troy",
            "Admin2": "AL",
            "Postal": "36081",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1501 Skyland Blvd E",
            "Admin1": "Tuscaloosa",
            "Admin2": "AL",
            "Postal": "35405",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "3501 20th Av",
            "Admin1": "Valley",
            "Admin2": "AL",
            "Postal": "36854",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "1300 Montgomery Highway",
            "Admin1": "Vestavia Hills",
            "Admin2": "AL",
            "Postal": "35216",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "4538 Us Hwy 231",
            "Admin1": "Wetumpka",
            "Admin2": "AL",
            "Postal": "36092",
            "CountryCode": "USA",
        }
    },
    {
        "address": {
            "Address": "2575 Us Hwy 43",
            "Admin1": "Winfield",
            "Admin2": "AL",
            "Postal": "35594",
            "CountryCode": "USA",
        }
    },
]
