import sys
from unittest.case import SkipTest

sys.path.insert(0, r"C:\\ipython_workfolder\\geosaurus\\src")
import unittest
import os
from arcgis.gis import GIS
from arcgis.mapping import SceneLayer

gis = GIS(profile="your_enterprise_profile")
scn_item = gis.content.get("43da12a04c314269a524b6b1c32cb2f5")
scn_lyr = SceneLayer(scn_item.url, gis)
mngr = scn_lyr.manager
mngr._tbx

# Initialize manager
online_admin = GIS(
    profile="your_online_profile",
    verify_cert=False,
)
# Scene Layer published from a Scene Layer Package
scene_layer_item = online_admin.content.get("48a3165121584b49bff6cf5150c8cdc3")
scene_layer = SceneLayer(scene_layer_item.url, online_admin)
manager = scene_layer.manager

# Scene Layer published through a Feature Service
fs_scene_layer_item = online_admin.content.get("ab5eddcefd024664bfa30e10d6027081")
fs_scene_layer = SceneLayer(fs_scene_layer_item.url, online_admin)
fs_manager = fs_scene_layer.manager


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

    def test_update_tiles(self):
        """
        Test update tiles
        """
        update = manager.update_tiles(levels="0-4")
        assert update

    def test_jobs(self):
        """
        Test various job functions
        """
        jobs = manager.jobs()
        assert jobs
        assert isinstance(jobs, dict)

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
        res = manager.edit_item(
            item = source_item_id
        )
        assert res
        assert res["status"] == "success"

    def test_rebuild_cache(self):
        """
        Test rebuild cache on a scene layer published from a feature service
        """
        res = fs_manager.rebuild_cache("0")
        assert res

if __name__ == "__main__":
    unittest.main()
