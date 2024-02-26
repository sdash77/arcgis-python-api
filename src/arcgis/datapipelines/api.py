from __future__ import annotations
from typing import Iterator
from functools import lru_cache
from arcgis.auth.tools import LazyLoader

from ._pipelines import DataPipelines, PipelineRun

_arcgis_gis = LazyLoader("arcgis.gis")

__all__ = ["list_runs", "run_data_pipeline"]


@lru_cache(maxsize=254)
def _get_arcgis_pipeline(
    gis: _arcgis_gis.GIS, version: float | int = 1.1
) -> DataPipelines:
    """gets the pipline from the GIS"""
    helper_service = gis.properties["helperServices"]

    if "dataPipelines" in helper_service:
        url: str = (
            f"{helper_service['dataPipelines']['url']}/api/v{version}/{gis.properties['id']}/"
        )
        return DataPipelines(url=url, gis=gis)
    return None


def list_runs(
    item: _arcgis_gis.Item, gis: _arcgis_gis.GIS | None = None
) -> Iterator[PipelineRun]:
    """
    Returns all running pipelines for a given Item.

    =================================================     ========================================================================
    **Parameter**                                         **Description**
    -------------------------------------------------     ------------------------------------------------------------------------
    item                                                  Required Item. The `Data Pipeline` type item to run.
    -------------------------------------------------     ------------------------------------------------------------------------
    gis                                                   Optional GIS. The WebGIS connection class used to run the `run_data_pipeline`
                                                          operation.  If the value is `None`, then the item's GIS object will be
                                                          used.
    =================================================     ========================================================================

    :return: Iterator[PipelineRun]
    """
    if gis is None:
        gis = item._gis
    pipeline: DataPipelines = _get_arcgis_pipeline(gis=gis)
    for run in pipeline.runs.query(item):
        yield run


def run_data_pipeline(
    item: _arcgis_gis.Item, gis: _arcgis_gis.GIS | None = None
) -> PipelineRun:
    """

    Allows a user to run a given data pipeline from a data pipeline item

    =================================================     ========================================================================
    **Parameter**                                         **Description**
    -------------------------------------------------     ------------------------------------------------------------------------
    item                                                  Required Item. The `Data Pipeline` type item to run.
    -------------------------------------------------     ------------------------------------------------------------------------
    gis                                                   Optional GIS. The WebGIS connection class used to run the `run_data_pipeline`
                                                          operation.  If the value is `None`, then the item's GIS object will be
                                                          used.
    =================================================     ========================================================================

    :return: PipelineRun
    """
    if gis is None:
        gis = item._gis

    pipeline: DataPipelines = _get_arcgis_pipeline(gis=gis)
    if pipeline is None:
        raise Exception(
            "Your organization or user account does not support Data Pipelines, please contact your Organization's administrator."
        )
    return pipeline.runs.create(item=item)
