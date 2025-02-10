"""
Tests the functionality of the knowledge graph
"""
import unittest
from arcgis.gis import GIS
from arcgis.geometry import Geometry
from arcgis.layers import Service
from typing import Generator
import requests
import uuid
from utils.decorators import integration_test

# change these variables as needed
# server_url should point to existent testing graph, if applicable
domain = "dev0025946.esri.com"
# server_url = domain + "/server/rest/services/Hosted/python_testing/KnowledgeGraphServer"
server_url = "https://dev0025946.esri.com/server/rest/services/Hosted/python_unit_testing/KnowledgeGraphServer"
portal_url = "https://dev0025946.esri.com/portal"
username = "publisher2"
password = "esri.agp123"


# shoutout Megan for putting this function together
def create_new_kg(domain, username, password, kg_name, gis):
    token = ""
    token_url = f"https://{domain}/portal/sharing/rest/generateToken"
    creds = {
        "username": username,
        "password": password,
        "referer": f"https://{domain}/portal",
        "f": "json",
    }
    token_response = gis._con._session.post(token_url, data=creds)
    try:
        token = token_response.json()["token"]
        url = f"https://{domain}/portal/sharing/rest/content/users/{username}/createService"  # replace domain and username with yours
        create = {
            "createParameters": f'{{"name": {kg_name},"capabilities": "Query", "jsonProperties": {{"supportsProvenance": true}}}}',
            "outputType": "KnowledgeGraph",
            "f": "json",
            "token": token,
        }
        create_response = gis._con._session.post(url, data=create)
        success = create_response.json()["success"]
        if success == True:
            print("Creation was successful:", create_response.json()["serviceurl"])
            return create_response.json()["serviceurl"]
        else:
            print("Creation failed:", create_response.json()["error"]["message"])
            return False
    except:
        print("Error in Creation")
        print(token_response.json()["error"]["message"])
        return False


try:
    from arcgis.graph import KnowledgeGraph

    gis = GIS(
        url=portal_url,
        username=username,
        password=password,
        verify_cert=False,
        trust_env=True,
    )
    print("Logged in as: " + gis.properties.user.username)
    try:
        kg = KnowledgeGraph(server_url, gis=gis)
        assert kg.datamodel != None
        print("Accessed existent testing graph")
        SKIP = False
    except:
        new_kg = create_new_kg(domain, username, password, "python_unit_testing", gis)
        kg = KnowledgeGraph(new_kg, gis=gis)
        print("Created new testing graph")
        SKIP = False

except:
    SKIP = True


@unittest.skipIf(SKIP, "Cannot login or get service")
@integration_test
class TestImport(unittest.TestCase):
    def test_import(self):
        from arcgis.graph import KnowledgeGraph

    def test_search(self):
        items = gis.content.search("type:Knowledge Graph")
        if len(items) > 0:
            assert isinstance(KnowledgeGraph.fromitem(items[0]), KnowledgeGraph)
    
    def test_service_init(self):
        s = Service(kg._url, gis)
        assert isinstance(s, KnowledgeGraph)
        

@unittest.skipIf(SKIP, "Cannot login or get service")
@integration_test
class TestKGMethods(unittest.TestCase):
    """tests the methods"""

    def test_simple_query(self):
        q = """MATCH (n) RETURN n.objectid, n.geometry, n LIMIT 10"""
        result = kg.query(query=q)  # "MATCH (n) RETURN n LIMIT 10")
        assert isinstance(result, (list, tuple))
        if len(result) > 0:
            assert isinstance(result[0], list)

    def test_query_streaming(self):
        # setup
        kg.named_object_type_adds(
            entity_types=[
                {
                    "name": "Pokemon",
                    "alias": "Pokemon",
                    "role": "esriGraphNamedObjectRegular",
                    "strict": False,
                    "properties": {
                        "name": {
                            "name": "name",
                            "role": "esriGraphPropertyRegular",
                        },
                        "shape": {
                            "name": "shape",
                            "fieldType": "esriFieldTypeGeometry",
                            "geometryType": "esriGeometryPolygon",
                            "role": "esriGraphPropertyRegular",
                        },
                    },
                }
            ]
        )
        char_uuid = f'{{{str(uuid.uuid4()).upper()}}}'
        snor_uuid = f'{{{str(uuid.uuid4()).upper()}}}'
        add_list = [
            {
                "_objectType": "entity",
                "_typeName": "Pokemon",
                "_id": char_uuid,
                "_properties": {
                    "name": "Charizard",
                },
            },
            {
                "_objectType": "entity",
                "_typeName": "Pokemon",
                "_id": snor_uuid,
                "_properties": {
                    "shape": {
                        "rings": [
                            [
                                [-76.920820633, 39.078453569000004],
                                [-76.921316371, 39.078093032000005],
                                [-76.921646863, 39.078419769],
                                [-76.92118117000001, 39.078795328000005],
                                [-76.920820633, 39.078453569000004],
                            ]
                        ],
                        "_objectType": "geometry",
                        "spatialReference": {"wkid": 4326},
                    },
                    "name": "Snorlax",
                    "globalid": snor_uuid,
                    "objectid": 2,
                },
            },
        ]

        add_res = kg.apply_edits(adds=add_list)

        # make sure our graph has stuff in it
        q = """MATCH (n) RETURN n.objectid, n.shape, n LIMIT 10"""
        result = kg.query_streaming(query=q)
        assert len(list(result)) > 0

        # primitive value bind parameter test
        with self.subTest(msg="Primitive bind test"):
            bind = {"param1": "Charizard"}
            query = """MATCH (n) WHERE n.name = $param1 RETURN n"""
            gen = kg.query_streaming(query=query, bind_param=bind)
            assert isinstance(gen, Generator)
            assert len(list(gen)) > 0

        # geometry bind parameter test
        with self.subTest(msg="Geometry bind test"):
            test_geom = Geometry(
                {
                    "rings": [
                        [
                            [-76.920820633, 39.078453569000004],
                            [-76.921316371, 39.078093032000005],
                            [-76.921646863, 39.078419769],
                            [-76.92118117000001, 39.078795328000005],
                            [-76.920820633, 39.078453569000004],
                        ]
                    ]
                }
            )
            bind2 = {"geom": test_geom}
            query2 = (
                """MATCH (n) WHERE esri.graph.ST_Intersects($geom, n.shape) RETURN n"""
            )
            gen2 = kg.query_streaming(query=query2, bind_param=bind2)
            assert isinstance(gen2, Generator)
            assert len(list(gen2)) > 0

        with self.subTest(msg="Simple object bind test"):
            bind = {"simple": {"name": "Snorlax"}}
            query = """MATCH (n) WHERE n.name = $simple.name RETURN n"""
            gen = kg.query_streaming(query=query, bind_param=bind)
            assert isinstance(gen, Generator)
            assert len(list(gen)) > 0

        with self.subTest(msg="List bind test"):
            bind = {"list": ["Snorlax", "Articuno"]}
            query = """MATCH (n) where n.name IN $list RETURN n"""
            gen = kg.query_streaming(query=query, bind_param=bind)
            assert isinstance(gen, Generator)
            assert len(list(gen)) > 0

        # test provenance in search
        with self.subTest(msg="Provenance inclusion test"):
            prov_uuid = f'{{{str(uuid.uuid4()).upper()}}}'
            prov_entity = {
                "_objectType": "entity",
                "_typeName": "Provenance",
                "_id": prov_uuid,
                "_properties": {
                    "instanceID": char_uuid,
                    "propertyName": "name",
                    "sourceType": "String",
                    "typeName": "Pokemon",
                    "sourceName": "MySourceName",
                    "source": "MySource",
                    "globalid": prov_uuid,
                },
            }
            kg.apply_edits(adds=[prov_entity])

            query3 = """MATCH (n) RETURN n.objectid, n.geometry, n LIMIT 10"""
            has_prov = kg.query_streaming(query=query3, include_provenance=True)
            no_prov = kg.query_streaming(query=query3)
            assert isinstance(has_prov, Generator)
            assert isinstance(no_prov, Generator)
            # query with provenance included should have more results than other
            assert len(list(has_prov)) > len(list(no_prov))
        
        # cleanup
        dels = {
                "_objectType": "entity",
                "_typeName": "Pokemon",
                "_ids": [char_uuid, snor_uuid],
        }
        kg.apply_edits(deletes=[dels], cascade_delete_provenance=True)

    def test_search(self):
        search = kg.search("China")
        assert isinstance(search, list)

    def test_validate_import(self):
        kg._validate_import()

    def test_update_search_index(self):
        props = {"Document": {"property_names": ["text"]}}
        kg.update_search_index(deletes=props)
        assert (
            "text"
            not in kg.datamodel["search_indexes"]["esri__search_idx"][
                "search_properties"
            ]["Document"]["property_names"]
        )
        kg.update_search_index(adds=props)
        assert (
            "text"
            in kg.datamodel["search_indexes"]["esri__search_idx"]["search_properties"][
                "Document"
            ]["property_names"]
        )

    def test_update_graph_property_index(self):
        # setup
        kg.named_object_type_adds(
            entity_types=[
                {
                    "name": "PokeCenter",
                    "alias": "PokeCenter",
                    "role": "esriGraphNamedObjectRegular",
                    "strict": False,
                    "properties": {
                        "name": {
                            "name": "name",
                            "role": "esriGraphPropertyRegular",
                        },
                        "shape": {
                            "name": "shape",
                            "fieldType": "esriFieldTypeGeometry",
                            "geometryType": "esriGeometryPolygon",
                            "role": "esriGraphPropertyRegular",
                        },
                        "city": {
                            "name": "city",
                            "role": "esriGraphPropertyRegular",
                        },
                    },
                }
            ]
        )

        assert "city" not in kg.datamodel["entity_types"]["PokeCenter"]["field_indexes"]

        with self.subTest(msg="Add test"):
            res = kg.graph_property_index_adds(
                "PokeCenter",
                [
                    {
                        "name": "city",
                        "isAscending": True,
                        "isUnique": True,
                        "fields": ["city"],
                    }
                ],
            )

            assert res
            assert res["indexAddResults "] == [{"name": "city"}]
            assert "city" in kg.datamodel["entity_types"]["PokeCenter"]["field_indexes"]

        with self.subTest(msg="Delete test"):
            res = kg.graph_property_index_deletes(
                "PokeCenter",
                ["city"],
            )

            assert res
            assert res["indexDeleteResults "] == [{"name": "city"}]
            assert (
                "city"
                not in kg.datamodel["entity_types"]["PokeCenter"]["field_indexes"]
            )

    def test_apply_edits(self):
        import time
        pika_uuid = f'{{{str(uuid.uuid4()).upper()}}}'
        with self.subTest(msg="Add test"):
            add_dict = {
                "_objectType": "entity",
                "_typeName": "Document",
                "_id": pika_uuid,
                "_properties": {
                    "name": "Pikachu",
                },
            }

            res = kg.apply_edits(adds=[add_dict])
            assert isinstance(res, dict)
            time.sleep(2)
            assert len(kg.search("Pikachu")) > 0

        with self.subTest(msg="Update test"):
            update_dict = {
                "_objectType": "entity",
                "_typeName": "Document",
                "_id": pika_uuid,
                "_properties": {
                    "name": "Raichu",
                },
            }

            res = kg.apply_edits(updates=[update_dict])
            assert isinstance(res, dict)
            time.sleep(2)
            assert len(kg.search("Raichu")) > 0

        with self.subTest(msg="Delete test"):
            delete_dict = {
                "_objectType": "entity",
                "_typeName": "Document",
                "_ids": [pika_uuid],
            }

            res = kg.apply_edits(deletes=[delete_dict])
            assert isinstance(res, dict)
            time.sleep(2)
            assert len(kg.search("Raichu")) == 0

        with self.subTest(msg="Provenance Test"):
            # we test this by seeing how many entities, including provenance, are in the graph
            # should be no more than a few entities in this graph, so limit of 20 is safe
            test_query = """MATCH (n) RETURN n.objectid, n.geometry, n LIMIT 20"""
            initial_amount = len(
                list(kg.query_streaming(query=test_query, include_provenance=True))
            )

            poli_uuid = f'{{{str(uuid.uuid4()).upper()}}}'
            prov_uuid = f'{{{str(uuid.uuid4()).upper()}}}'
            # test adding provenance
            adds_list = [
                {
                    "_objectType": "entity",
                    "_typeName": "Document",
                    "_id": poli_uuid,
                    "_properties": {
                        "name": "Poliwhirl",
                    },
                },
                {
                    "_objectType": "entity",
                    "_typeName": "Provenance",
                    "_id": prov_uuid,
                    "_properties": {
                        "instanceID": poli_uuid,
                        "propertyName": "name",
                        "sourceType": "String",
                        "typeName": "Document",
                        "sourceName": "MySourceName",
                        "source": "MySource",
                        "globalid": prov_uuid,
                    },
                },
            ]
            res = kg.apply_edits(adds=adds_list)
            assert isinstance(res, dict)
            time.sleep(1)
            second_amount = len(
                list(kg.query_streaming(query=test_query, include_provenance=True))
            )
            # should have two more entities in it
            assert (second_amount - initial_amount) == 2

            # test cascade deleting provenance
            delete_dict = {
                "_objectType": "entity",
                "_typeName": "Document",
                "_ids": [poli_uuid],
            }
            res = kg.apply_edits(deletes=[delete_dict], cascade_delete_provenance=True)
            assert isinstance(res, dict)
            final_amount = len(
                list(kg.query_streaming(query=test_query, include_provenance=True))
            )
            # call should have deleted both entities, making it equal to initial again
            assert final_amount == initial_amount

    def test_constraint_rules(self):

        with self.subTest(msg="Add test"):

            pokemon = {"set": ["Pokemon"]}

            healed_at = {"set": ["HealedAt"]}

            pokecenter = {"set_complement": ["PokeCenter"]}

            relationship_exclusion_rule = {
                "origin_entity_types": pokemon,
                "relationship_types": healed_at,
                "destination_entity_types": pokecenter,
            }

            constraint_rule = {
                "name": "PokemonCS",
                "alias": "pokecenterdata",
                "disabled": False,
                "relationship_exclusion_rule": relationship_exclusion_rule,
            }

            res = kg.constraint_rule_adds([constraint_rule])
            assert isinstance(res, dict)
            assert "PokemonCS" in kg.datamodel["constraint_rules"]

        with self.subTest(msg="Update Test"):

            constraint_rule = {
                "name": "PokemonCS",
                "alias": "gymdata",
                "disabled": False,
            }

            mask = {
                "update_name": False,
                "update_alias": True,
                "update_disabled": True
            }

            relationship_exclusion_rule_update =  {
                "update_origin_entity_types": {
                    "add_named_types": ["Trainer"],
                    "remove_named_types": ["Pokemon"]
                },
                "update_relationship_types": {
                    "add_named_types": ["TrainedAt"],
                    "remove_named_types": ["HealedAt"]
                },
                "update_destination_entity_types": {
                    "add_named_types": ["Gym"],
                    "remove_named_types": ["PokeCenter"]
                }
            }

            constraint_rule_update = {
                "rule_name": "PokemonCS",
                "mask": mask,
                "constraint_rule": constraint_rule,
                "relationship_exclusion_rule_update": relationship_exclusion_rule_update
            }

            res = kg.constraint_rule_updates([constraint_rule_update])
            assert isinstance(res, dict)
            assert "PokemonCS" in kg.datamodel['constraint_rules']
            assert kg.datamodel['constraint_rules']['PokemonCS']['alias'] == 'gymdata'

        with self.subTest(msg="Delete Test"):

            res = kg.constraint_rule_deletes(["PokemonCS"])
            assert isinstance(res, dict)
            assert "PokemonCS" not in kg.datamodel["constraint_rules"]


@unittest.skipIf(SKIP, "Cannot login or get service")
@integration_test
class TestKGService(unittest.TestCase):
    """tests the properties"""

    def test_datamodel(self):
        """tests getting the datamodel"""
        dm = kg.datamodel
        assert isinstance(dm, dict)

    def test_properties(self):
        props = kg.properties
        assert props


if __name__ == "__main__":
    unittest.main()
