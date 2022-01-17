import sys
from unittest.case import SkipTest

sys.path.insert(0, r"C:\\ipython_workfolder\\geosaurus_main\\src")
import unittest
import os
from arcgis.gis import GIS
from arcgis.mapping import SceneLayer

# Initialize manager
online_admin = GIS(
    profile="your_dev_profile",
    verify_cert=False,
)
scene_layer_item = online_admin.content.get("579cb30cfa234518906f34bc10577f3e")
scene_layer = SceneLayer(scene_layer_item.sourceUrl, online_admin)
manager = scene_layer.manager


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

    def test_edit_tile_service(self):
        """
        Test edit tile service.
        """
        source_item_id = scene_layer_item.related_items(
            rel_type="Service2Data", direction="forward"
        )[0]["id"]
        res = manager.edit_tile_service(
            service_name="Stockholm_SE_i3s",
            source_item_id=source_item_id,
            export_tiles_allowed=True,
            max_export_tile_count=5000,
        )
        assert res
        assert res["status"] == "success"


if __name__ == "__main__":
    unittest.main()
