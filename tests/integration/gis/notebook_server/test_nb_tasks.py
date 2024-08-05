import unittest
from arcgis.gis.tasks import TaskManager, Task
from arcgis.gis.tasks import Run
from utils.decorators import integration_test, profiles


@profiles.admin_enterprise
@integration_test
class TestListAllTasks(unittest.TestCase):
    """
    tests get tasks from user search and scheduled_tasks for notebook server, enterprise must be 10.8.1+
    """

    def test_user_search(self):
        """tests list all tasks through User"""
        tasks = self.gis.users.me.tasks
        assert isinstance(tasks, TaskManager)
        assert isinstance(
            tasks.search(types="ExecuteNotebook,UpdateInsightsWorkbook"), list
        )

    def test_list_all_tasks(self):
        """tests list all the tasks through PortalAdminManager"""
        st = self.gis.admin.scheduled_tasks
        assert isinstance(list(st()), list)
        assert isinstance(list(st(user=self.gis.users.me)), list)
        assert isinstance(list(st(active=False)), list)
        assert isinstance(list(st(active=True)), list)
        assert isinstance(
            list(st(
                types="ExecuteNotebook,UpdateInsightsWorkbook",
            )),
            list,
        )


@integration_test
@profiles.admin_enterprise
class TestUserScheduleTaskManager(unittest.TestCase):
    """test Task Manager for notebook server in gis.tasks submodule, enterprise must be 10.8.1+"""

    def test_task_properties(self):
        """tests the task's properties"""
        user = self.gis.users.me
        st = user.tasks
        isinstance(st, TaskManager)
        if len(st.all) > 0:
            task = st.all[0]
            assert task.properties
        else:
            items = self.gis.content.search(
                "owner: %s" % self.gis.users.me.username, item_type="Notebook"
            )
            if len(items) > 0:
                task = st.create(
                    title="props_test",
                    task_type="ExecuteNotebook",
                    item=items[0],
                    cron="2 2 2 2 ?",
                )
                assert task.properties
                task.delete()

    def test_enable(self):
        """test the Task's Enable/Disable method"""
        user = self.gis.users.me
        st = user.tasks
        items = self.gis.content.search(
            "owner: %s" % user.username, item_type="Notebook"
        )

        if len(items) > 0:
            task = st.create(
                title="props_test",
                task_type="ExecuteNotebook",
                item=items[0],
                cron="2 2 2 2 ?",
            )
            assert task.enable(enabled=True)
            assert task.enable(enabled=False)
            task.delete()

    def test_update(self):
        """test the Task's update method"""
        user = self.gis.users.me
        items = self.gis.content.search(
            "owner: %s" % user.username, item_type="Notebook"
        )
        st = user.tasks
        if len(items) > 0:
            item = items[0]
            itemid = item.itemid
            t1 = st.create(task_type="ExecuteNotebook", item=item, cron="* * * * ?")
            assert isinstance(t1, Task)
            t1.update(title="TESTUPDATE")
            assert t1.properties.title == "TESTUPDATE"
            assert t1.delete()

    def test_create_delete(self):
        """tests creating and deleting a scheduled task"""
        user = self.gis.users.me
        st = user.tasks
        isinstance(st, TaskManager)
        items = self.gis.content.search(
            "owner: %s" % self.gis.users.me.username, item_type="Notebook"
        )
        if len(items) > 0:

            item = items[0]
            itemid = item.itemid
            t1 = st.create(
                title="t1", task_type="ExecuteNotebook", item=item, cron="* * * * ?"
            )
            assert isinstance(t1, Task)
            assert t1.delete()
            t2 = st.create(
                title="t2", task_type="ExecuteNotebook", item=itemid, cron="0 1 2 12 ?"
            )
            assert isinstance(t2, Task)
            assert t2.delete()

    def test_isinstance(self):
        """tests the isinstance checks for the scheduling"""
        user = self.gis.users.me
        assert user.tasks
        assert isinstance(user.tasks, TaskManager)
        assert isinstance(user.tasks.count, int)
        assert isinstance(user.tasks.all, list)
        if len(user.tasks.all) > 0:
            task_list = user.tasks.all
            task = task_list[0]
            assert isinstance(task, Task)
            runs = task.runs
            assert isinstance(runs, list)
            if len(runs) > 0:
                assert isinstance(runs[0], Run)
                runs[0].properties


if __name__ == "__main__":
    unittest.main()
