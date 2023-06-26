from __future__ import annotations
import os
import json
import tempfile
import concurrent.futures
from typing import Any
from arcgis.gis import GIS, Group, GroupManager
from arcgis.auth.tools import LazyLoader
from functools import lru_cache
from arcgis.gis.clone._base import BaseCloneGroup

_arcgis = LazyLoader("arcgis")


###########################################################################
class CloningJob:
    """
    A Single Group Cloning Job

    This class should not be created by users.
    """

    _future: concurrent.futures.Future
    _task: str

    # ---------------------------------------------------------------------
    def __init__(self, future: concurrent.futures.Future, task: str = "Group") -> None:
        self._future = future
        self._task = task

    # ---------------------------------------------------------------------
    def __str__(self) -> str:
        return f"< {self._task} Cloning Job: {self.status} >"

    # ---------------------------------------------------------------------
    def __repr__(self) -> str:
        return self.__str__()

    # ---------------------------------------------------------------------
    @property
    def status(self) -> bool:
        """checks if the job completed"""
        return self._future.done()

    # ---------------------------------------------------------------------
    def cancel(self) -> bool:
        """checks if the job completed"""
        return self._future.cancel()

    # ---------------------------------------------------------------------
    def result(self) -> Group:
        """returns a group"""
        return self._future.result()

    # ---------------------------------------------------------------------
    @property
    def running(self) -> bool:
        """checks if the job was cancelled"""
        return self._future.running()

    # ---------------------------------------------------------------------
    @property
    def cancelled(self) -> bool:
        """checks if the job was cancelled"""
        return self._future.cancelled()


###########################################################################
class GroupCloner(BaseCloneGroup):
    """
    The `GroupCloner` allows users to copy Groups from one organization to another.

    Once the groups are copied, the `clone_items` or Group Migration Manager can be
    used to add the data.

    """

    _group_source: Group = None
    _include_items: bool = None
    _gis: GIS = None
    _out_folder: str | None = None
    _tracker: dict[str, Any] | None = None
    _tp: concurrent.futures.ThreadPoolExecutor = None

    def __init__(
        self,
        *,
        gis: GIS | None = None,
    ) -> None:
        """initializer"""
        super()
        if gis:
            self._gis: GIS = gis
        elif _arcgis.env.active_env:
            self._gis = _arcgis.env.active_env
        else:
            raise ValueError("The `GIS` object is not defined.")

        self._tp = concurrent.futures.ThreadPoolExecutor(max_workers=10)

    # ---------------------------------------------------------------------
    def __str__(self) -> str:
        return "< Group Cloner >"

    # ---------------------------------------------------------------------
    def __repr__(self) -> str:
        return "< Group Cloner >"

    # ---------------------------------------------------------------------
    @lru_cache(maxsize=100)
    def _setup_group_project_folder(
        self, group_id: str, out_folder: str | None = None
    ) -> str:
        """creates a group project folder"""
        if out_folder:
            os.makedirs(out_folder, exist_ok=True)
        elif out_folder is None:
            out_folder = os.path.join(tempfile.gettempdir(), group_id)
            os.makedirs(out_folder, exist_ok=True)
        self._out_folder = out_folder
        return out_folder

    # ---------------------------------------------------------------------
    def _check_if_exists(self, group: Group) -> bool:
        """Checks if the group exists on the destination org"""
        results = self._gis.groups.search(f"id: {group.id}")
        return len(results) >= 1

    # ---------------------------------------------------------------------
    def _process(self, params) -> Group:
        """
        Runs the clone process on a single group entry
        """
        thumbnail: str = self._get_thumbnail(
            group=params["group"], save_folder=params["working_folder"]
        )
        group: Group = params["group"]
        mgr: GroupManager = params["gis"].groups
        lu = {
            '{"itemTypes": "Application"}': "apps",
            '{"itemTypes": ""}': None,
            '{"itemTypes": "CSV"}': "files",
            '{"itemTypes": "Web Map"}': "maps",
            '{"itemTypes": "Layer"}': "layers",
            '{"itemTypes": "Web Scene"}': "scenes",
            '{"itemTypes": "Locator Package"}': "tools",
        }
        display_settings = None
        if json.dumps(group.displaySettings) in lu:
            display_settings = lu[json.dumps(group.displaySettings)]
        tags: list[str] = group.tags
        tags.append(f"cloned_source_id: {group.id}")
        group = mgr.create(
            title=group.title,
            tags=group.tags,
            description=group.description,
            snippet=group.snippet,
            thumbnail=thumbnail,
            is_invitation_only=group.isInvitationOnly,
            sort_field=group.sortField,
            sort_order=group.sortOrder,
            is_view_only=group.isViewOnly,
            auto_join=group.autoJoin,
            display_settings=display_settings,
            leaving_disallowed=group.leavingDisallowed,
            membership_access=getattr(group, "membershipAccess", None),
            hidden_members=getattr(group, "hiddenMembers", None),
            autojoin=group.autoJoin,
        )
        return group

    # ---------------------------------------------------------------------
    def _get_thumbnail(self, group: Group, save_folder: str) -> str:
        """
        downloads the thumbnail

        :returns: str
        """
        return group.download_thumbnail(save_folder=save_folder)

    # ---------------------------------------------------------------------
    def _run_ops(self, parameters: dict[str, Any]) -> CloningJob:
        """runs the job asynchronously."""
        jobs = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as tp:
            for key, params in parameters.items():
                future: concurrent.futures.Future = tp.submit(
                    self._process, **{"params": params}
                )
                jobs.append(CloningJob(future=future))
                del key, params
            tp.shutdown(wait=True)
        return jobs

    # ---------------------------------------------------------------------
    def clone(
        self, groups: list[Group], *, skip_existing: bool = True
    ) -> list[CloningJob]:
        """
        Override the clone operation in order performs the cloning logic
        """
        self._tracker: dict[str, Any] = {}
        ## 1). Check Existance and setup project
        ##
        for group in groups:
            if (
                self._check_if_exists(group=group) == False and skip_existing
            ) or skip_existing == False:
                self._tracker[group.id] = {
                    "group": group,
                    "gis": self._gis,
                    "exists": self._check_if_exists(group),
                    "working_folder": self._setup_group_project_folder(
                        group_id=group.id
                    ),
                }
        return self._run_ops(parameters=self._tracker)
