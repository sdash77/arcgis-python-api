from unittest.case import SkipTest
import unittest
import os
from arcgis.gis import GIS
from arcgis.layers import VectorTileLayer, VectorTileLayerManager
from utils.decorators import integration_test

# Initialize manager
online_admin = GIS(profile="your_online_admin_profile", verify_cert=False)

# Item published from Service Directory
sd_vector_tile_item = online_admin.content.get("90ff63ae7ecb4bfd9bc6aec2f88d5230")
sd_tile_layer = VectorTileLayer.fromitem(sd_vector_tile_item)
sd_vtl_manager = sd_tile_layer.manager

# Item published from FeatureService
fs_vector_tile_item = online_admin.content.get("90ff63ae7ecb4bfd9bc6aec2f88d5230")
fs_tile_layer = VectorTileLayer.fromitem(fs_vector_tile_item)
fs_vtl_manager = fs_tile_layer.manager


@integration_test
class TestVectorTileLayerManager_SD(unittest.TestCase):
    def test_refresh(self):
        """
        Test refresh
        """
        sd_res = sd_vtl_manager.refresh()
        assert sd_res

    @SkipTest
    def test_status(self):
        sd_status = sd_vtl_manager.status()
        assert sd_status

    def test_update_tiles(self):
        """
        Test update tiles
        """
        sd_update = sd_vtl_manager.update_tiles(merge_bundle=False)
        assert sd_update

    def test_jobs(self):
        """
        Test various job functions
        """
        ###### Test for SD VTL #######
        jobs = sd_vtl_manager.jobs()
        assert jobs
        assert isinstance(jobs, dict)

        # get the job id for a job
        job_id = jobs["jobs"][0]["id"]
        # get stats for a job
        stats = sd_vtl_manager.job_statistics(job_id=job_id)
        assert stats
        assert isinstance(stats, dict)

        # cancel a job
        try:
            cancel = sd_vtl_manager.cancel_job(job_id=job_id)
            assert cancel
        except:
            print(
                "Unable to cancel the job since the job {job_id} is in 'Done' state.".format(
                    job_id=job_id
                )
            )

        # rerun job
        try:
            re_run = sd_vtl_manager.rerun_job(code="ALL", job_id=job_id)
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
        source_item_id = sd_vtl_manager.related_items(
            rel_type="Service2Data", direction="forward"
        )[0]["id"]
        sd_res = sd_vtl_manager.edit_tile_service(
            source_item_id=source_item_id,
            export_tiles_allowed=True,
            max_export_tile_count=5000,
        )
        assert sd_res
        assert sd_res["status"] == "success"


@integration_test
class TestVectorTileLayerManager_FS(unittest.TestCase):
    def test_refresh(self):
        """
        Test refresh
        """
        fs_res = fs_vtl_manager.refresh()
        assert fs_res

    @SkipTest
    def test_status(self):
        fs_status = fs_vtl_manager.status()
        assert fs_status

    def test_update_tiles(self):
        """
        Test update tiles
        """
        fs_update = fs_vtl_manager.update_tiles()
        assert fs_update

    def test_jobs(self):
        """
        Test various job functions
        """
        ############ Test for FS VTL ###############
        jobs = fs_vtl_manager.jobs()
        assert jobs
        assert isinstance(jobs, dict)

        # get the job id for a job
        job_id = jobs["jobs"][0]["id"]
        # get stats for a job
        stats = fs_vtl_manager.job_statistics(job_id=job_id)
        assert stats
        assert isinstance(stats, dict)

        # cancel a job
        try:
            cancel = fs_vtl_manager.cancel_job(job_id=job_id)
            assert cancel
        except:
            print(
                "Unable to cancel the job since the job {job_id} is in 'Done' state.".format(
                    job_id=job_id
                )
            )

        # rerun job
        try:
            re_run = fs_vtl_manager.rerun_job(code="ALL", job_id=job_id)
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
        fs_res = fs_vtl_manager.edit_tile_service(max_zoom=23)
        assert fs_res
        assert fs_res["status"] == "success"


if __name__ == "__main__":
    unittest.main()
