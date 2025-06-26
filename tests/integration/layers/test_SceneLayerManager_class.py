from unittest.case import SkipTest
import unittest
import os
from arcgis.gis import GIS
from arcgis.layers import SceneLayer
from utils.decorators import integration_test

# Initialize manager
online_admin = GIS(
    profile="your_online_api_data_owner_profile",
    verify_cert=False,
)

# Scene Layer published from a Scene Layer Package
scene_layer_item = online_admin.content.get("d30897c3e97b4a1d8a9b3be7ee7599e6")
scene_layer = SceneLayer(scene_layer_item.url, online_admin)
manager = scene_layer.manager

# Scene Layer published through a Feature Service
fs_scene_layer_item = online_admin.content.get("d30897c3e97b4a1d8a9b3be7ee7599e6")
fs_scene_layer = SceneLayer(fs_scene_layer_item.url, online_admin)
fs_manager = fs_scene_layer.manager



@integration_test
class TestSceneLayerManager(unittest.TestCase):
    def test_refresh(self):
        """
        Test refresh
        """
        res = manager.refresh()
        assert res

    @SkipTest
    def test_status(self):
        status = manager.status()
        assert status

    def test_jobs(self):
        """
        Test various job functions
        """
        jobs = manager.jobs()
        assert jobs
        assert isinstance(jobs, dict)

        if not jobs["jobs"]:
            print("No jobs available for the scene layer.")
            return
        # get the job id for a job
        job_id = jobs["jobs"][0]["id"]
        # get stats for a job
        stats = manager.job_statistics(job_id=job_id)
        assert stats
        assert isinstance(stats, dict)

        # cancel a job
        try:
            cancel = manager.cancel_job(job_id=job_id)
            assert cancel
        except:
            print(
                "Unable to cancel the job since the job {job_id} is in 'Done' state.".format(
                    job_id=job_id
                )
            )

        # rerun job
        try:
            re_run = manager.rerun_job(code="ALL", job_id=job_id)
            assert re_run
        except:
            print(
                "Unable to rerun the job since the job {job_id} is in 'Done' state.".format(
                    job_id=job_id
                )
            )

    def test_edit_item(self):
        """
        Test edit item.
        """
        source_item_id = scene_layer_item.related_items(
            rel_type="Service2Data", direction="forward"
        )[0]["id"]
        res = manager.edit(item=source_item_id)
        assert res
        assert res.get("status") == "success", res

    def test_rebuild_cache(self):
        """
        Test rebuild cache on a scene layer published from a feature service
        """
        res = manager.rebuild_cache("0")
        if res:
            # could be none
            assert res


if __name__ == "__main__":
    unittest.main()
