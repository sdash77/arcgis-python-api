"""
This is 10.8.1+ Functionality Tests for Notebook Server
"""
import sys
sys.path.insert(0, r"C:\SVN\achapkowski_geosaurus_fork_issue_5663\src")
import unittest
import os, json
import arcgis
from arcgis.gis import GIS
from arcgis.gis.nb import NotebookServer, NotebookManager
from arcgis.gis.tasks._schedule import TaskManager, Task
from arcgis.gis.tasks._schedule import Run
try:
    url = "https://datasciencedev.esri.com/portal"
    username = "portaladmin"
    password = 'esri.agp'
    gis = GIS(url=url, username=username, password=password, verify_cert=False, trust_env=True)
    SKIP_TESTS = False
except:
    SKIP_TESTS = True
###########################################################################
@unittest.skipIf(SKIP_TESTS == True,
                 "Cannot connect to Testing Server and/or Portal")
class TestGISAdminAllTasks1081(unittest.TestCase):
    #----------------------------------------------------------------------
    def test_user_search(self):
        tasks = gis.users.me.tasks
        assert isinstance(tasks, TaskManager)
        assert isinstance(tasks.search(types="ExecuteNotebook,UpdateInsightsWorkbook"), list)
    #----------------------------------------------------------------------
    def test_list_all_tasks(self):
        """tests listing all the tasks"""
        st = gis.admin.scheduled_tasks
        #assert st()
        assert isinstance(st(), list)
        assert isinstance(st(user=gis.users.me), list)
        assert isinstance(st(active=False), list)
        assert isinstance(st(active=True), list)
        assert isinstance(st(types="ExecuteNotebook,UpdateInsightsWorkbook",), list)
###########################################################################
@unittest.skipIf(SKIP_TESTS == True,
                 "Cannot connect to Testing Server and/or Portal")
class TestUserScheduleTasks1081(unittest.TestCase):
    #----------------------------------------------------------------------
    def test_task_properties(self):
        """tests the task's properties"""
        user = gis.users.me
        st = user.tasks
        isinstance(st, TaskManager)
        if len(st.all) > 0:
            task = st.all[0]
            assert task.properties
        else:
            items = gis.content.search("owner: %s" % gis.users.me.username, item_type='Notebook')
            if len(items) > 0:
                task = st.create(title='props_test', task_type="ExecuteNotebook", item=items[0], cron='2 2 2 2 ?')
                assert task.properties
                task.delete()
    #----------------------------------------------------------------------
    def test_enable(self):
        """test the Task's Enable/Disable method"""
        user = gis.users.me
        st = user.tasks
        items = gis.content.search("owner: %s" % user.username, item_type='Notebook')

        if len(items) > 0:
            task = st.create(title='props_test', task_type="ExecuteNotebook", item=items[0], cron='2 2 2 2 ?')
            assert task.enable(enabled=True)
            assert task.enable(enabled=False)
            task.delete()
    #----------------------------------------------------------------------
    def test_update(self):
        """test the Task's update method"""
        user = gis.users.me
        items = gis.content.search("owner: %s" % user.username, item_type='Notebook')
        st = user.tasks
        if len(items) > 0:
            item = items[0]
            itemid = item.itemid
            t1 = st.create(task_type="ExecuteNotebook", item=item, cron='* * * * ?')
            assert isinstance(t1, Task)
            t1.update(title='TESTUPDATE')
            assert t1.properties.title == 'TESTUPDATE'
            assert t1.delete()
    #----------------------------------------------------------------------
    def test_create_delete(self):
        """tests creating and deleting a scheduled task"""
        user = gis.users.me
        st = user.tasks
        isinstance(st, TaskManager)
        items = gis.content.search("owner: %s" % gis.users.me.username, item_type='Notebook')
        if len(items) > 0:

            item = items[0]
            itemid = item.itemid
            t1 = st.create(title='t1', task_type="ExecuteNotebook", item=item, cron='* * * * ?')
            assert isinstance(t1, Task)
            assert t1.delete()
            t2 = st.create(title='t2', task_type="ExecuteNotebook", item=itemid, cron='0 1 2 12 ?')
            assert isinstance(t2, Task)
            assert t2.delete()
    #----------------------------------------------------------------------
    def test_isinstance(self):
        """tests the isinstance checks for the scheduling"""
        user = gis.users.me
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
@unittest.skipIf(SKIP_TESTS == True,
                 "Cannot connect to Testing Server and/or Portal")
class TestNotebookServer1081(unittest.TestCase):
    """Tests New 10.8.1 Functionality"""
    #----------------------------------------------------------------------
    def test_recent_stats(self):
        """tests the recent statistics"""
        servers = gis.admin.servers.list()
        for server in gis.admin.servers.list():
            if isinstance(server, NotebookServer):
                break
        assert server.system.recent_statistics
        assert isinstance(server.system.recent_statistics, dict)

@unittest.skipIf(SKIP_TESTS == True,
                 "Cannot connect to Testing Server and/or Portal")
class TestNotebookServer109(unittest.TestCase):
    """Tests New 10.9 Functionality"""
    #----------------------------------------------------------------------
    def test_list_jobs(self):
        """tests the `list_jobs` method added at 10.9"""
        servers = gis.admin.servers.list()
        for server in gis.admin.servers.list():
            if isinstance(server, NotebookServer):
                break
        assert server.system.list_jobs()
        assert server.system.list_jobs(details=False)
        assert server.system.list_jobs(details=True)
        assert server.system.list_jobs(details=True, num=5)
        assert server.system.list_jobs(details=False, num=5)

if __name__ == "__main__":
    unittest.main()