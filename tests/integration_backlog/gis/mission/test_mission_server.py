import unittest
import os
from arcgis.gis import GIS
from arcgis.gis.mission import MissionServer, Mission, MissionCatalog, MissionJob
from arcgis.gis.mission._logs import LogManager
from arcgis.gis.mission._system import SystemManager
from arcgis.gis.mission._machines import MachineManager
from arcgis.gis.mission._security import SecurityManager
import time
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging


enable_verbose_logging()


@profiles.admin_enterprise
@integration_test
class TestMissionServer(unittest.TestCase):
    def test_properties(self):
        """
        Test the properties of the mission server
        """
        mission_server = MissionServer("https://pythonapitestnb.dev.geocloud.com/missionserver", self.gis)
        assert mission_server

        info = mission_server.info
        assert info

        logs = mission_server.logs
        assert isinstance(logs, LogManager)

        system = mission_server.system
        assert isinstance(system, SystemManager)

        machine = mission_server.machine
        assert isinstance(machine, MachineManager)

        security = mission_server.security
        assert isinstance(security, SecurityManager)


@profiles.enterprise
@integration_test
class TestMission(unittest.TestCase):
    def test_properties(self):
        mission_ctlg = MissionCatalog(self.gis)
        assert mission_ctlg

        assert mission_ctlg.properties

    def test_mission(self):
        mission_ctlg = MissionCatalog(self.gis)
        mission_job = mission_ctlg.create_mission(title="Python API Test Mission")
        assert isinstance(mission_job, MissionJob)
        # wait for job to finish
        time.sleep(20)

        # get the mission created for the test
        for m in mission_ctlg.missions:
            if m.properties["title"] == "Python API Test Mission":
                mission = m
        assert isinstance(mission, Mission)

        # add report
        report = mission.add_report(
            title="Python API Test Mission Report",
            service_name="PythonAPIReport",
            questions=[
                {
                    "isRequired": True,
                    "fieldName": "damage_description",
                    "defaultValue": "",
                    "name": "multi_line_text",
                    "description": "Multiline Text Field used to describe the damage",
                    "id": "field_2",
                    "position": 1,
                    "label": "Describe the damage",
                    "type": "esriQuestionTypeTextArea",
                },
                {
                    "isRequired": False,
                    "fieldName": "damage_level",
                    "defaultValue": "single_choice_1",
                    "name": "single_choice",
                    "description": "Select a level of damage.",
                    "id": "field_3",
                    "position": 2,
                    "label": "Label for selecting a level of damage",
                    "type": "esriQuestionTypeSingleChoice",
                    "choices": {
                        "items": [
                            {
                                "label": "This is option 1",
                                "position": 0,
                                "value": "single_choice_1",
                            },
                            {
                                "label": "This is option 2",
                                "position": 1,
                                "value": "single_choice_2",
                            },
                        ]
                    },
                },
                {
                    "isRequired": False,
                    "fieldName": "date_time_occured",
                    "name": "date_time",
                    "description": "Select a Date and Time when the damage approx. occured",
                    "id": "field_4",
                    "position": 3,
                    "label": "Date and Time damage occured",
                    "type": "esriQuestionTypeDateTime",
                },
                {
                    "isRequired": False,
                    "fieldName": "team_reported",
                    "defaultValue": "",
                    "name": "dropdown",
                    "description": "Select a team that reported the damage",
                    "id": "field_5",
                    "position": 4,
                    "label": "Reported by team:",
                    "type": "esriQuestionTypeDropdown",
                    "choices": {
                        "items": [
                            {
                                "label": "Team Alpha",
                                "position": 0,
                                "value": "dropdown_choice_1",
                            },
                            {
                                "label": "Team Bravo",
                                "position": 1,
                                "value": "dropdown_choice_2",
                            },
                        ]
                    },
                },
            ],
        )
        assert report
        assert report["success"] is True

        assert self.gis.content.get(report["reportItemId"]).delete()
        # test delete
        assert mission.delete()


if __name__ == "__main__":
    unittest.main()
