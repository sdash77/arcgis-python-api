from arcgis.gis.kubernetes._admin._base import _BaseKube
from arcgis.gis import GIS

###########################################################################
class TaskManager(_BaseKube):
    """
    Provides access to the tasks resources defined on the ArcGIS
    Enterprise.
    """

    _gis = None
    _con = None
    _properties = None
    _url = None

    def __init__(self, url: str, gis: GIS):
        super()
        self._url = url
        self._gis = gis
        self._con = gis._con

    # ---------------------------------------------------------------------
    def task(self, task_id: str):
        """
        This operation returns information on a specific task, such as the task's title, parameters, and schedule.
        """
        url = f"{self._url}/{task_id}"
        params = {"f": "json"}
        return self._con.get(url, params)

    # ---------------------------------------------------------------------
    def edit_task(
        self,
        task_id: str,
        title,
        type,
        parameters,
        item_id,
        start_date,
        end_date,
        minute,
        hour,
        day_of_month,
        month,
        day_of_week,
        max_occurences,
    ):
        """
        This operation allows you to edit and update the properties of a preexisting task
        (CleanGPJobs, BackupRetentionCleaner at 10.9.1, and CreateBackup at 10.9.1).
        Updates that have been made to a task will go into effect during its next scheduled execution.
        """
        url = f"{self._url}/{task_id}/update"
        params = {"f": "json"}
        # Add parameters that are input
        return self._con.get(url, params)

    # ---------------------------------------------------------------------
    def delete_task(self, task_id: str):
        """
        This operation deletes a task. Once the task is deleted, all associated runs and
        resources are deleted as well.
        """
        url = f"{self._url}/{task_id}/delete"
        params = {"f": "json"}
        return self._con.post(url, params)

    # ---------------------------------------------------------------------
    def enable_task(self, task_id: str):
        """
        This operation enables a previously disabled task,
        setting its taskState to active.
        """
        url = f"{self._url}/{task_id}/enable"
        params = {"f": "json"}
        return self._con.post(url, params)

    # ---------------------------------------------------------------------
    def diable_task(self, task_id: str):
        """
        This operation disables a specific task and suspends any
        upcoming runs scheduled for the task.
        """
        url = f"{self._url}/{task_id}/disable"
        params = {"f": "json"}
        return self._con.post(url, params)

    # ---------------------------------------------------------------------
    def runs(self, task_id: str):
        """
        This resource returns a list of all runs that have been completed for a
        specific task.
        """
        url = f"{self._url}/{task_id}/runs"
        params = {"f": "json"}
        return self._con.get(url, params)

    # ---------------------------------------------------------------------
    def run(self, task_id: str, run_id: str):
        """
        This resource returns information on a specific run for a task.
        """
        url = f"{self._url}/{task_id}/runs/{run_id}"
        params = {"f": "json"}
        return self._con.get(url, params)

    # ---------------------------------------------------------------------
    def edit_run(self, task_id: str, run_id: str, status, results):
        """
        This operation updates an existing run for a scheduled task.
        """
        url = f"{self._url}/{task_id}/runs/{run_id}/update"
        params = {"f": "json", "status": status, "results": results}
        return self._con.post(url, params)

    # ---------------------------------------------------------------------
    def delete_run(self, task_id: str, run_id: str):
        """
        The delete operation removes a specified run for a scheduled task.
        Deleting a run also deletes corresponding resource files associated with the run.
        """
        url = f"{self._url}/{task_id}/runs/{run_id}/delete"
        params = {"f": "json"}
        return self._con.post(url, params)

    # ---------------------------------------------------------------------
    def create_task(
        self,
        type: str,
        parameters: dict,
        minute,
        hour,
        day_of_month,
        month,
        day_of_week,
        title,
        start_date,
        end_date,
        max_occurence,
    ):
        """
        This operation creates scheduled tasks for your deployment that run
        automatically. Once the task has been created, it can be updated using
        the Update operation. In addition, scheduled tasks can be disabled, reenabled,
        and deleted through other operations in the ArcGIS Enterprise Administrator API.
        """
        url = f"{self._url}/createTask"
        params = {
            "f": "json",
            "type": type,
            "parameters": parameters,
            "minute": minute,
            "hour": hour,
            "dayOfMonth": day_of_month,
            "month": month,
            "dayOfWeek": day_of_week,
        }
        if title:
            params["title"] = title
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self._con.post(url, params)
