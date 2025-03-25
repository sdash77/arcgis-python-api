import unittest
from arcgis.layers._ogc import WMTSLayer

class TestWmtsLayer(unittest.TestCase):
    def test_get_dict_from_xml(self):
        """Tests converting xml to dictionary"""
        wmts_dict = WMTSLayer._get_dict_from_xml(world_time_zones_wmts_xml)
        assert wmts_dict
        assert "Capabilities" in wmts_dict
    
    def test_get_operational_layer_config_with_n_gt_1_tile_matrix_set(self):
        """Tests getting operational layer configuration, with n>1 TileMatrixSet config"""
        wmts_dict = WMTSLayer._get_dict_from_xml(world_time_zones_wmts_xml)
        operational_layer_config = WMTSLayer._get_operational_layer_config(world_time_zones_wmts_url, wmts_dict)
        assert operational_layer_config
        assert operational_layer_config.get("wmtsInfo", {}).get("layerIdentifier") == "WorldTimeZones"
    
    def test_get_operational_layer_config_single_tile_matrix_set(self):
        """Tests getting operational layer configuration, with single TileMatrixSet config"""
        wmts_dict = WMTSLayer._get_dict_from_xml(holderbank_wmts_xml)
        operational_layer_config = WMTSLayer._get_operational_layer_config(holderbank_wmts_url, wmts_dict)
        assert operational_layer_config
        assert operational_layer_config.get("wmtsInfo", {}).get("layerIdentifier") == "holderbank_holderbank_abwasser"

holderbank_wmts_url = "https://map.infogis2.ch/arcgis/rest/services/holderbank/holderbank_abwasser/MapServer/WMTS"
holderbank_wmts_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Capabilities xmlns="http://www.opengis.net/wmts/1.0"
    xmlns:ows="http://www.opengis.net/ows/1.1"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:gml="http://www.opengis.net/gml"
    xsi:schemaLocation="http://www.opengis.net/wmts/1.0 http://schemas.opengis.net/wmts/1.0/wmtsGetCapabilities_response.xsd"
    version="1.0.0">
    <!-- Service Identification -->
    <ows:ServiceIdentification>
        <ows:Title>holderbank_holderbank_abwasser</ows:Title>
        <ows:ServiceType>OGC WMTS</ows:ServiceType>
        <ows:ServiceTypeVersion>1.0.0</ows:ServiceTypeVersion>
    </ows:ServiceIdentification> <!--
    Operations Metadata -->
    <ows:OperationsMetadata>
        <ows:Operation name="GetCapabilities">
            <ows:DCP>
                <ows:HTTP>
                    <ows:Get
                        xlink:href="https://map.infogis2.ch/arcgis/rest/services/holderbank/holderbank_abwasser/MapServer/WMTS/1.0.0/WMTSCapabilities.xml">
                        <ows:Constraint name="GetEncoding">
                            <ows:AllowedValues>
                                <ows:Value>RESTful</ows:Value>
                            </ows:AllowedValues>
                        </ows:Constraint>
                    </ows:Get>
                    <!-- add KVP binding in 10.1 -->
                    <ows:Get
                        xlink:href="https://map.infogis2.ch/arcgis/rest/services/holderbank/holderbank_abwasser/MapServer/WMTS?">
                        <ows:Constraint name="GetEncoding">
                            <ows:AllowedValues>
                                <ows:Value>KVP</ows:Value>
                            </ows:AllowedValues>
                        </ows:Constraint>
                    </ows:Get>
                </ows:HTTP>
            </ows:DCP>
        </ows:Operation>
        <ows:Operation name="GetTile">
            <ows:DCP>
                <ows:HTTP>
                    <ows:Get
                        xlink:href="https://map.infogis2.ch/arcgis/rest/services/holderbank/holderbank_abwasser/MapServer/WMTS/tile/1.0.0/">
                        <ows:Constraint name="GetEncoding">
                            <ows:AllowedValues>
                                <ows:Value>RESTful</ows:Value>
                            </ows:AllowedValues>
                        </ows:Constraint>
                    </ows:Get>
                    <ows:Get
                        xlink:href="https://map.infogis2.ch/arcgis/rest/services/holderbank/holderbank_abwasser/MapServer/WMTS?">
                        <ows:Constraint name="GetEncoding">
                            <ows:AllowedValues>
                                <ows:Value>KVP</ows:Value>
                            </ows:AllowedValues>
                        </ows:Constraint>
                    </ows:Get>
                </ows:HTTP>
            </ows:DCP>
        </ows:Operation>
    </ows:OperationsMetadata>
    <Contents>
        <!--Layer-->
        <Layer>
            <ows:Title>holderbank_holderbank_abwasser</ows:Title>
            <ows:Identifier>holderbank_holderbank_abwasser</ows:Identifier>
            <ows:BoundingBox crs="urn:ogc:def:crs:EPSG::2056">
                <ows:LowerCorner>2621027.5207693875 1239803.697894816</ows:LowerCorner>
                <ows:UpperCorner>2627033.5744481613 1244423.332134084</ows:UpperCorner>
            </ows:BoundingBox>
            <ows:WGS84BoundingBox crs="urn:ogc:def:crs:OGC:2:84">
                <ows:LowerCorner>7.717699739535361 47.309921381614274</ows:LowerCorner>
                <ows:UpperCorner>7.79741552359364 47.35169585503656</ows:UpperCorner>
            </ows:WGS84BoundingBox>
            <Style isDefault="true">
                <ows:Title>Default Style</ows:Title>
                <ows:Identifier>default</ows:Identifier>
            </Style>
            <Format>image/png</Format>
            <TileMatrixSetLink>
                <TileMatrixSet>default028mm</TileMatrixSet>
            </TileMatrixSetLink>
            <ResourceURL format="image/png" resourceType="tile"
                template="https://map.infogis2.ch/arcgis/rest/services/holderbank/holderbank_abwasser/MapServer/WMTS/tile/1.0.0/holderbank_holderbank_abwasser/{Style}/{TileMatrixSet}/{TileMatrix}/{TileRow}/{TileCol}.png" />
        </Layer> <!--TileMatrixSet-->
        <TileMatrixSet>
            <ows:Title>TileMatrix using 0.28mm</ows:Title>
            <ows:Abstract>The tile matrix set that has scale values calculated based on the dpi
                defined by OGC specification (dpi assumes 0.28mm as the physical distance of a
                pixel).</ows:Abstract>
            <ows:Identifier>default028mm</ows:Identifier>
            <ows:SupportedCRS>urn:ogc:def:crs:EPSG::2056</ows:SupportedCRS>
            <TileMatrix>
                <ows:Identifier>0</ows:Identifier>
                <ScaleDenominator>472471.18303754483</ScaleDenominator>
                <TopLeftCorner>-2.9380010775807664E7 3.500843066123094E7</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>946</MatrixWidth>
                <MatrixHeight>998</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>1</ows:Identifier>
                <ScaleDenominator>283482.7098225269</ScaleDenominator>
                <TopLeftCorner>-2.9380010775807664E7 3.500843066123094E7</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>1576</MatrixWidth>
                <MatrixHeight>1662</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>2</ows:Identifier>
                <ScaleDenominator>141741.35491126345</ScaleDenominator>
                <TopLeftCorner>-2.9380010775807664E7 3.500843066123094E7</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>3151</MatrixWidth>
                <MatrixHeight>3324</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>3</ows:Identifier>
                <ScaleDenominator>70870.67745563173</ScaleDenominator>
                <TopLeftCorner>-2.9380010775807664E7 3.500843066123094E7</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>6301</MatrixWidth>
                <MatrixHeight>6648</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>4</ows:Identifier>
                <ScaleDenominator>47247.118303754476</ScaleDenominator>
                <TopLeftCorner>-2.9380010775807664E7 3.500843066123094E7</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>9451</MatrixWidth>
                <MatrixHeight>9972</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>5</ows:Identifier>
                <ScaleDenominator>23623.559151877238</ScaleDenominator>
                <TopLeftCorner>-2.9380010775807664E7 3.500843066123094E7</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>18902</MatrixWidth>
                <MatrixHeight>19943</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>6</ows:Identifier>
                <ScaleDenominator>9449.423660750896</ScaleDenominator>
                <TopLeftCorner>-2.9380010775807664E7 3.500843066123094E7</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>47255</MatrixWidth>
                <MatrixHeight>49856</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>7</ows:Identifier>
                <ScaleDenominator>4724.711830375448</ScaleDenominator>
                <TopLeftCorner>-2.9380010775807664E7 3.500843066123094E7</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>94509</MatrixWidth>
                <MatrixHeight>99711</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>8</ows:Identifier>
                <ScaleDenominator>1889.8847321501792</ScaleDenominator>
                <TopLeftCorner>-2.9380010775807664E7 3.500843066123094E7</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>236273</MatrixWidth>
                <MatrixHeight>249276</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>9</ows:Identifier>
                <ScaleDenominator>944.9423660750896</ScaleDenominator>
                <TopLeftCorner>-2.9380010775807664E7 3.500843066123094E7</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>472545</MatrixWidth>
                <MatrixHeight>498552</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>10</ows:Identifier>
                <ScaleDenominator>472.4711830375448</ScaleDenominator>
                <TopLeftCorner>-2.9380010775807664E7 3.500843066123094E7</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>945089</MatrixWidth>
                <MatrixHeight>997104</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>11</ows:Identifier>
                <ScaleDenominator>188.9884732150179</ScaleDenominator>
                <TopLeftCorner>-2.9380010775807664E7 3.500843066123094E7</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>2362721</MatrixWidth>
                <MatrixHeight>2492758</MatrixHeight>
            </TileMatrix>
        </TileMatrixSet>
    </Contents>
    <ServiceMetadataURL
        xlink:href="https://map.infogis2.ch/arcgis/rest/services/holderbank/holderbank_abwasser/MapServer/WMTS/1.0.0/WMTSCapabilities.xml" />
</Capabilities>
"""

world_time_zones_wmts_url = "https://sampleserver6.arcgisonline.com/arcgis/rest/services/WorldTimeZones/MapServer/WMTS"
world_time_zones_wmts_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Capabilities xmlns="http://www.opengis.net/wmts/1.0"
    xmlns:ows="http://www.opengis.net/ows/1.1"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:gml="http://www.opengis.net/gml"
    xsi:schemaLocation="http://www.opengis.net/wmts/1.0 http://schemas.opengis.net/wmts/1.0/wmtsGetCapabilities_response.xsd"
    version="1.0.0">
    <!-- Service Identification -->
    <ows:ServiceIdentification>
        <ows:Title>WorldTimeZones</ows:Title>
        <ows:ServiceType>OGC WMTS</ows:ServiceType>
        <ows:ServiceTypeVersion>1.0.0</ows:ServiceTypeVersion>
    </ows:ServiceIdentification> <!--
    Operations Metadata -->
    <ows:OperationsMetadata>
        <ows:Operation name="GetCapabilities">
            <ows:DCP>
                <ows:HTTP>
                    <ows:Get
                        xlink:href="https://sampleserver6.arcgisonline.com/arcgis/rest/services/WorldTimeZones/MapServer/WMTS/1.0.0/WMTSCapabilities.xml">
                        <ows:Constraint name="GetEncoding">
                            <ows:AllowedValues>
                                <ows:Value>RESTful</ows:Value>
                            </ows:AllowedValues>
                        </ows:Constraint>
                    </ows:Get>
                    <!-- add KVP binding in 10.1 -->
                    <ows:Get
                        xlink:href="https://sampleserver6.arcgisonline.com/arcgis/rest/services/WorldTimeZones/MapServer/WMTS?">
                        <ows:Constraint name="GetEncoding">
                            <ows:AllowedValues>
                                <ows:Value>KVP</ows:Value>
                            </ows:AllowedValues>
                        </ows:Constraint>
                    </ows:Get>
                </ows:HTTP>
            </ows:DCP>
        </ows:Operation>
        <ows:Operation name="GetTile">
            <ows:DCP>
                <ows:HTTP>
                    <ows:Get
                        xlink:href="https://sampleserver6.arcgisonline.com/arcgis/rest/services/WorldTimeZones/MapServer/WMTS/tile/1.0.0/">
                        <ows:Constraint name="GetEncoding">
                            <ows:AllowedValues>
                                <ows:Value>RESTful</ows:Value>
                            </ows:AllowedValues>
                        </ows:Constraint>
                    </ows:Get>
                    <ows:Get
                        xlink:href="https://sampleserver6.arcgisonline.com/arcgis/rest/services/WorldTimeZones/MapServer/WMTS?">
                        <ows:Constraint name="GetEncoding">
                            <ows:AllowedValues>
                                <ows:Value>KVP</ows:Value>
                            </ows:AllowedValues>
                        </ows:Constraint>
                    </ows:Get>
                </ows:HTTP>
            </ows:DCP>
        </ows:Operation>
    </ows:OperationsMetadata>
    <Contents>
        <!--Layer-->
        <Layer>
            <ows:Title>WorldTimeZones</ows:Title>
            <ows:Identifier>WorldTimeZones</ows:Identifier>
            <ows:BoundingBox crs="urn:ogc:def:crs:EPSG::3857">
                <ows:LowerCorner>-2.0037507842788246E7 -3.0240971958386146E7</ows:LowerCorner>
                <ows:UpperCorner>2.0037507842788246E7 3.024097145838615E7</ows:UpperCorner>
            </ows:BoundingBox>
            <ows:WGS84BoundingBox crs="urn:ogc:def:crs:OGC:2:84">
                <ows:LowerCorner>-179.99999550841463 -88.99999992161116</ows:LowerCorner>
                <ows:UpperCorner>179.99999550841463 88.99999992161116</ows:UpperCorner>
            </ows:WGS84BoundingBox>
            <Style isDefault="true">
                <ows:Title>Default Style</ows:Title>
                <ows:Identifier>default</ows:Identifier>
            </Style>
            <Format>image/png</Format>
            <TileMatrixSetLink>
                <TileMatrixSet>default028mm</TileMatrixSet>
            </TileMatrixSetLink>
            <TileMatrixSetLink>
                <!--Only
                show this TileMatrixSet if the tiling scheme is compliant to Google Maps (and that
                happens with tile width = 256 px)-->
                <TileMatrixSet>GoogleMapsCompatible</TileMatrixSet>
            </TileMatrixSetLink>
            <ResourceURL format="image/png" resourceType="tile"
                template="https://sampleserver6.arcgisonline.com/arcgis/rest/services/WorldTimeZones/MapServer/WMTS/tile/1.0.0/WorldTimeZones/{Style}/{TileMatrixSet}/{TileMatrix}/{TileRow}/{TileCol}.png" />
        </Layer> <!--TileMatrixSet-->
        <TileMatrixSet>
            <ows:Title>TileMatrix using 0.28mm</ows:Title>
            <ows:Abstract>The tile matrix set that has scale values calculated based on the dpi
                defined by OGC specification (dpi assumes 0.28mm as the physical distance of a
                pixel).</ows:Abstract>
            <ows:Identifier>default028mm</ows:Identifier>
            <ows:SupportedCRS>urn:ogc:def:crs:EPSG::3857</ows:SupportedCRS>
            <TileMatrix>
                <ows:Identifier>0</ows:Identifier>
                <ScaleDenominator>5.590822640285016E8</ScaleDenominator>
                <TopLeftCorner>-2.0037508342787E7 2.0037508342787E7</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>1</MatrixWidth>
                <MatrixHeight>2</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>1</ows:Identifier>
                <ScaleDenominator>2.7954113201425034E8</ScaleDenominator>
                <TopLeftCorner>-2.0037508342787E7 2.0037508342787E7</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>2</MatrixWidth>
                <MatrixHeight>3</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>2</ows:Identifier>
                <ScaleDenominator>1.3977056600712562E8</ScaleDenominator>
                <TopLeftCorner>-2.0037508342787E7 2.0037508342787E7</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>4</MatrixWidth>
                <MatrixHeight>6</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>3</ows:Identifier>
                <ScaleDenominator>6.988528300356235E7</ScaleDenominator>
                <TopLeftCorner>-2.0037508342787E7 2.0037508342787E7</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>8</MatrixWidth>
                <MatrixHeight>11</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>4</ows:Identifier>
                <ScaleDenominator>3.494264150178117E7</ScaleDenominator>
                <TopLeftCorner>-2.0037508342787E7 2.0037508342787E7</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>16</MatrixWidth>
                <MatrixHeight>21</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>5</ows:Identifier>
                <ScaleDenominator>1.7471320750890587E7</ScaleDenominator>
                <TopLeftCorner>-2.0037508342787E7 2.0037508342787E7</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>32</MatrixWidth>
                <MatrixHeight>41</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>6</ows:Identifier>
                <ScaleDenominator>8735660.375445293</ScaleDenominator>
                <TopLeftCorner>-2.0037508342787E7 2.0037508342787E7</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>64</MatrixWidth>
                <MatrixHeight>81</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>7</ows:Identifier>
                <ScaleDenominator>4367830.187722647</ScaleDenominator>
                <TopLeftCorner>-2.0037508342787E7 2.0037508342787E7</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>128</MatrixWidth>
                <MatrixHeight>161</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>8</ows:Identifier>
                <ScaleDenominator>2183915.0938617955</ScaleDenominator>
                <TopLeftCorner>-2.0037508342787E7 2.0037508342787E7</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>256</MatrixWidth>
                <MatrixHeight>322</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>9</ows:Identifier>
                <ScaleDenominator>1091957.5469304253</ScaleDenominator>
                <TopLeftCorner>-2.0037508342787E7 2.0037508342787E7</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>512</MatrixWidth>
                <MatrixHeight>643</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>10</ows:Identifier>
                <ScaleDenominator>545978.7734656851</ScaleDenominator>
                <TopLeftCorner>-2.0037508342787E7 2.0037508342787E7</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>1024</MatrixWidth>
                <MatrixHeight>1285</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>11</ows:Identifier>
                <ScaleDenominator>272989.38673237007</ScaleDenominator>
                <TopLeftCorner>-2.0037508342787E7 2.0037508342787E7</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>2048</MatrixWidth>
                <MatrixHeight>2570</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>12</ows:Identifier>
                <ScaleDenominator>136494.69336618503</ScaleDenominator>
                <TopLeftCorner>-2.0037508342787E7 2.0037508342787E7</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>4096</MatrixWidth>
                <MatrixHeight>5139</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>13</ows:Identifier>
                <ScaleDenominator>68247.34668309252</ScaleDenominator>
                <TopLeftCorner>-2.0037508342787E7 2.0037508342787E7</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>8192</MatrixWidth>
                <MatrixHeight>10278</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>14</ows:Identifier>
                <ScaleDenominator>34123.67334154626</ScaleDenominator>
                <TopLeftCorner>-2.0037508342787E7 2.0037508342787E7</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>16384</MatrixWidth>
                <MatrixHeight>20556</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>15</ows:Identifier>
                <ScaleDenominator>17061.836671245605</ScaleDenominator>
                <TopLeftCorner>-2.0037508342787E7 2.0037508342787E7</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>32768</MatrixWidth>
                <MatrixHeight>41112</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>16</ows:Identifier>
                <ScaleDenominator>8530.918335622802</ScaleDenominator>
                <TopLeftCorner>-2.0037508342787E7 2.0037508342787E7</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>65536</MatrixWidth>
                <MatrixHeight>82223</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>17</ows:Identifier>
                <ScaleDenominator>4265.459167338929</ScaleDenominator>
                <TopLeftCorner>-2.0037508342787E7 2.0037508342787E7</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>131072</MatrixWidth>
                <MatrixHeight>164445</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>18</ows:Identifier>
                <ScaleDenominator>2132.729584141936</ScaleDenominator>
                <TopLeftCorner>-2.0037508342787E7 2.0037508342787E7</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>262144</MatrixWidth>
                <MatrixHeight>328889</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>19</ows:Identifier>
                <ScaleDenominator>1066.3647915984968</ScaleDenominator>
                <TopLeftCorner>-2.0037508342787E7 2.0037508342787E7</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>524288</MatrixWidth>
                <MatrixHeight>657777</MatrixHeight>
            </TileMatrix>
        </TileMatrixSet>
        <TileMatrixSet>
            <ows:Title>GoogleMapsCompatible</ows:Title>
            <ows:Abstract>the wellknown 'GoogleMapsCompatible' tile matrix set defined by OGC WMTS
                specification</ows:Abstract>
            <ows:Identifier>GoogleMapsCompatible</ows:Identifier>
            <ows:SupportedCRS>urn:ogc:def:crs:EPSG:6.18.3:3857</ows:SupportedCRS>
            <WellKnownScaleSet>urn:ogc:def:wkss:OGC:1.0:GoogleMapsCompatible</WellKnownScaleSet>
            <TileMatrix>
                <ows:Identifier>0</ows:Identifier>
                <ScaleDenominator>559082264.0287178</ScaleDenominator>
                <TopLeftCorner>-20037508.34278925 20037508.34278925</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>1</MatrixWidth>
                <MatrixHeight>1</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>1</ows:Identifier>
                <ScaleDenominator>279541132.0143589</ScaleDenominator>
                <TopLeftCorner>-20037508.34278925 20037508.34278925</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>2</MatrixWidth>
                <MatrixHeight>2</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>2</ows:Identifier>
                <ScaleDenominator>139770566.0071794</ScaleDenominator>
                <TopLeftCorner>-20037508.34278925 20037508.34278925</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>4</MatrixWidth>
                <MatrixHeight>4</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>3</ows:Identifier>
                <ScaleDenominator>69885283.00358972</ScaleDenominator>
                <TopLeftCorner>-20037508.34278925 20037508.34278925</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>8</MatrixWidth>
                <MatrixHeight>8</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>4</ows:Identifier>
                <ScaleDenominator>34942641.50179486</ScaleDenominator>
                <TopLeftCorner>-20037508.34278925 20037508.34278925</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>16</MatrixWidth>
                <MatrixHeight>16</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>5</ows:Identifier>
                <ScaleDenominator>17471320.75089743</ScaleDenominator>
                <TopLeftCorner>-20037508.34278925 20037508.34278925</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>32</MatrixWidth>
                <MatrixHeight>32</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>6</ows:Identifier>
                <ScaleDenominator>8735660.375448715</ScaleDenominator>
                <TopLeftCorner>-20037508.34278925 20037508.34278925</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>64</MatrixWidth>
                <MatrixHeight>64</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>7</ows:Identifier>
                <ScaleDenominator>4367830.187724357</ScaleDenominator>
                <TopLeftCorner>-20037508.34278925 20037508.34278925</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>128</MatrixWidth>
                <MatrixHeight>128</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>8</ows:Identifier>
                <ScaleDenominator>2183915.093862179</ScaleDenominator>
                <TopLeftCorner>-20037508.34278925 20037508.34278925</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>256</MatrixWidth>
                <MatrixHeight>256</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>9</ows:Identifier>
                <ScaleDenominator>1091957.546931089</ScaleDenominator>
                <TopLeftCorner>-20037508.34278925 20037508.34278925</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>512</MatrixWidth>
                <MatrixHeight>512</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>10</ows:Identifier>
                <ScaleDenominator>545978.7734655447</ScaleDenominator>
                <TopLeftCorner>-20037508.34278925 20037508.34278925</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>1024</MatrixWidth>
                <MatrixHeight>1024</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>11</ows:Identifier>
                <ScaleDenominator>272989.3867327723</ScaleDenominator>
                <TopLeftCorner>-20037508.34278925 20037508.34278925</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>2048</MatrixWidth>
                <MatrixHeight>2048</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>12</ows:Identifier>
                <ScaleDenominator>136494.6933663862</ScaleDenominator>
                <TopLeftCorner>-20037508.34278925 20037508.34278925</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>4096</MatrixWidth>
                <MatrixHeight>4096</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>13</ows:Identifier>
                <ScaleDenominator>68247.34668319309</ScaleDenominator>
                <TopLeftCorner>-20037508.34278925 20037508.34278925</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>8192</MatrixWidth>
                <MatrixHeight>8192</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>14</ows:Identifier>
                <ScaleDenominator>34123.67334159654</ScaleDenominator>
                <TopLeftCorner>-20037508.34278925 20037508.34278925</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>16384</MatrixWidth>
                <MatrixHeight>16384</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>15</ows:Identifier>
                <ScaleDenominator>17061.83667079827</ScaleDenominator>
                <TopLeftCorner>-20037508.34278925 20037508.34278925</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>32768</MatrixWidth>
                <MatrixHeight>32768</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>16</ows:Identifier>
                <ScaleDenominator>8530.918335399136</ScaleDenominator>
                <TopLeftCorner>-20037508.34278925 20037508.34278925</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>65536</MatrixWidth>
                <MatrixHeight>65536</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>17</ows:Identifier>
                <ScaleDenominator>4265.459167699568</ScaleDenominator>
                <TopLeftCorner>-20037508.34278925 20037508.34278925</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>131072</MatrixWidth>
                <MatrixHeight>131072</MatrixHeight>
            </TileMatrix>
            <TileMatrix>
                <ows:Identifier>18</ows:Identifier>
                <ScaleDenominator>2132.729583849784</ScaleDenominator>
                <TopLeftCorner>-20037508.34278925 20037508.34278925</TopLeftCorner>
                <TileWidth>256</TileWidth>
                <TileHeight>256</TileHeight>
                <MatrixWidth>262144</MatrixWidth>
                <MatrixHeight>262144</MatrixHeight>
            </TileMatrix>
        </TileMatrixSet>
    </Contents>
    <ServiceMetadataURL
        xlink:href="https://sampleserver6.arcgisonline.com/arcgis/rest/services/WorldTimeZones/MapServer/WMTS/1.0.0/WMTSCapabilities.xml" />
</Capabilities>
"""

if __name__ == "__main__":
    unittest.main()