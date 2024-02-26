from __future__ import annotations
import time
import logging
from typing import Any, Iterator
from arcgis.auth.tools import LazyLoader
from arcgis.auth import EsriSession
import requests
from ._enums import RunStatus
from cachetools import cached, TTLCache

_arcgis_gis = LazyLoader("arcgis.gis")

_log = logging.getLogger()


###########################################################################
class PipelineRun:
    """
    Represents a **single** run of a `Data Pipeline` process execution.

    ===============     ====================================================================
    **Parameter**        **Description**
    ---------------     --------------------------------------------------------------------
    url                 Required String. The `url` of the data pipeline endpoint.
    ---------------     --------------------------------------------------------------------
    session             Required EsriSession. The connection object.
    ===============     ====================================================================


    """

    url: str
    sesssion: EsriSession
    _properties: dict[str, Any] | None = None

    # ---------------------------------------------------------------------
    def __init__(self, url: str, session: EsriSession) -> None:
        """initializer"""
        self.url: str = url
        self.session: EsriSession = session

    # ---------------------------------------------------------------------
    @property
    def properties(self) -> dict[str, Any]:
        """
        Returns the properties of the run


        :returns: dict[str,Any]
        """
        if self._properties is None:
            resp: requests.Response = self.session.get(
                url=self.url,
                params={
                    "f": "json",
                },
            )
            resp.raise_for_status()
            res: dict[str, Any] = resp.json()
            self._properties = res
        return self._properties

    # ---------------------------------------------------------------------
    @property
    def result(self) -> dict[str, Any]:
        """
        Gets the run results. This operation will pause the thread when called
        until the pipeline finishes.

        :returns: dict[str,Any]
        """
        i: int = 1

        status: RunStatus = self.status
        while isinstance(status, RunStatus) and status in [
            RunStatus.WAITING,
            RunStatus.SUBMITTED,
            RunStatus.CANCELLING,
            RunStatus.RUNNING,
        ]:
            _log.warning(
                f"Waiting for the `Run` to resolve it's finalized status: {self.status.value}"
            )
            time.sleep(i * 2)
            if i <= 5:
                i += 1
            status: RunStatus = self.status
        url: str = f"{self.url}/result"
        params: dict[str, Any] = {"f": "json"}
        resp: requests.Response = self.session.get(url=url, params=params)
        resp.raise_for_status()
        return resp.json()

    # ---------------------------------------------------------------------
    def cancel(self) -> bool:
        """
        Terminates the current run.

        :returns:bool
        """
        url: str = f"{self.url}/cancel"
        params: dict[str, Any] = {
            "f": "json",
        }
        resp: requests.Response = self.session.post(url=url, data=params)
        resp.raise_for_status()
        return resp.json().get("status", False)

    # ---------------------------------------------------------------------
    @property
    @cached(cache=TTLCache(maxsize=1024, ttl=5))
    def status(self) -> RunStatus | dict[str, Any]:
        """
        Checks the Job's status

        :returns: RunStatus | dict[str, Any]

        """
        url: str = f"{self.url}/status"
        params: dict[str, Any] = {"f": "json"}
        resp: requests.Response = self.session.get(url=url, params=params)
        resp.raise_for_status()
        res: dict[str, Any] = resp.json()
        if "status" in res:
            return RunStatus(res.get("status"))
        elif "error" in res:
            return RunStatus.FAILED
        return resp.json()


###########################################################################
class PipelineRuns:
    """
    Manager class used to work with data pipeline runs

    ===============     ====================================================================
    **Parameter**        **Description**
    ---------------     --------------------------------------------------------------------
    url                 Required String. The `url` of the pipeline endpoint.
    ---------------     --------------------------------------------------------------------
    session             Required EsriSession. The connection object.
    ===============     ====================================================================

    """

    session: EsriSession
    url: str

    # ---------------------------------------------------------------------
    def __init__(self, url: str, session: EsriSession) -> None:
        """initializer"""
        self.url: str = url
        self.session: EsriSession = session

    # ---------------------------------------------------------------------
    def create(self, item: _arcgis_gis.Item) -> PipelineRun:
        """
        Creates a new `Run` of a data pipeline

        ===============     ====================================================================
        **Parameter**        **Description**
        ---------------     --------------------------------------------------------------------
        item                Required Item. The `Data Pipeline` to examine.
        ===============     ====================================================================

        :returns: `PipelineRun`

        """
        if item.type != "Data Pipeline":
            raise ValueError("The `item` must be a `Data Pipeline` item.")
        url: str = f"{self.url}"
        params: dict[str, Any] = {"f": "json", "itemId": item.id}
        resp: requests.Response = self.session.post(url=url, data=params)
        resp.raise_for_status()
        data: dict[str, Any] = resp.json()
        if data.get("id", None):
            run_url: str = f"{self.url}/{data.get('id')}"
            return PipelineRun(url=run_url, session=self.session)
        return data

    # ---------------------------------------------------------------------
    def query(self, item: _arcgis_gis.Item) -> Iterator[PipelineRun]:
        """
        Returns all the `PipelineRun` objects on a given Data Pipeline item.

        ===============     ====================================================================
        **Parameter**        **Description**
        ---------------     --------------------------------------------------------------------
        item                Required Item. The `Data Pipeline` to examine.
        ===============     ====================================================================

        :returns: Iterator[PipelineRun]
        """
        if item.type != "Data Pipeline":
            raise ValueError("The `item` must be a `Data Pipeline` item.")
        url: str = f"{self.url}"
        params: dict[str, Any] = {"f": "json", "itemId": item.id}
        resp: requests.Response = self.session.get(url=url, params=params)
        resp.raise_for_status()
        has_more: str = resp.headers.get("X-Esri-Continuation", None)

        for run in resp.json().get("results", []):
            task_id: str = run.get("id", None)
            if task_id:
                run_url: str = f"{self.url}/{task_id}"
                yield PipelineRun(url=run_url, session=self.session)
        while has_more:
            resp: requests.Response = self.session.get(
                url=url,
                data=params,
                headers={"X-Esri-Continuation": has_more},
            )
            resp.raise_for_status()
            has_more: str = resp.headers.get("X-Esri-Continuation", None)
            data: dict[str, Any] = resp.json()
            for run in data.get("results", []):
                task_id: str = run.get("id", None)
                if task_id:
                    run_url: str = f"{self.url}/{task_id}"
                    yield PipelineRun(url=run_url, session=self.session)
            if len(data.get("results", [])) == 0:
                break


###########################################################################
class DataPipelines:
    """
    The beta Python API for the ArcGIS Data Pipeline

    ===============     ====================================================================
    **Parameter**        **Description**
    ---------------     --------------------------------------------------------------------
    url                 Required String. The `url` of the pipeline endpoint.
    ---------------     --------------------------------------------------------------------
    gis                 Required GIS. The `GIS` object that represents the current organization.
    ===============     ====================================================================

    """

    _gis: _arcgis_gis.GIS
    url: str
    session: EsriSession | None = None
    _runs: PipelineRuns | None = None

    def __init__(self, url: str, gis: _arcgis_gis.GIS):
        """initializer"""
        self.url = url
        self._gis = gis
        self.session = self._gis.session

    # ---------------------------------------------------------------------
    @property
    def runs(self) -> PipelineRuns:
        """
        Returns the `Runs` manager

        :returns: PipelineRuns
        """
        if self._runs is None:
            url: str = f"{self.url}runs"
            self._runs = PipelineRuns(url=url, session=self.session)
        return self._runs
