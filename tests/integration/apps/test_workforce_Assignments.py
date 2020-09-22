#-------------------------------------------------------------------------------
# Name:        Workforce Assignments tests
# Purpose:     Sanity tests for ArcGIS Python API
#-------------------------------------------------------------------------------
import unittest
from integration.dino_utils.dino_precondition_checks import PreconditionChecks
from integration.dino_utils.dino_configs import DinoConfigs
from configparser import ConfigParser
import datetime

#region PreCondition check
test_skip = False
class_skip = False
module_skip = False

r1 = PreconditionChecks.check_API_import()
r2 = PreconditionChecks.check_Python_version()

if (r1 & r2):
    print("## Precondition checks passed ##")
    module_skip = False
else:
    module_skip = True
    print("Pre condition checks failed. Quitting tests")
    raise(exit())

# Import the module after Precondition checks pass
try:
    from arcgis.gis import GIS, Group, User
    from arcgis.features import Feature, FeatureLayer
    from arcgis.mapping import WebMap
    from arcgis.apps.workforce import *
    from arcgis.apps.workforce._schemas import *
    from arcgis.apps.workforce.managers import *
except ImportError:
    print("API import error. Quitting test")
    raise(exit())
#endregion PreCondition Check

#TestModule
@unittest.skipIf(module_skip, "Precondition check failed. Skipping tests in Workforce Assignments")
def setUpModule():
    """
    Run checks for host system
    """
    # Get environment status
    print("ArcPy on system: " , PreconditionChecks.check_ArcPy_import())
    print("Is Pro installed: ", PreconditionChecks.check_Pro_installed())
    print("Host OS: " + PreconditionChecks.get_OS())


class Test_Workforce_Assignments_With_Assignments(unittest.TestCase):
    """
    Test to verify that assignments can be queried, added, updated, and deleted
    """

    def add_unassigned_assignment(self):
        self.project.assignments.add(
                                assignment_type=self.project.assignment_types.get(name="Inspection"),
                                status="unassigned",
                                geometry={"x": 123, "y": 456},
                                location="there",
                                description="Do some work",
                                dispatcher=self.dispatcher)

    def add_assigned_assignment(self):
        self.project.assignments.add(
            assignment_type=self.project.assignment_types.get(name="Removal"),
            status="assigned",
            geometry={"x": 123, "y": 456},
            location="there",
            description="Do some work",
            dispatcher=self.dispatcher,
            worker=self.worker,
            assigned_date=datetime.datetime(2018, 4, 16)
        )

    def add_completed_assignment(self):
        self.project.assignments.add(
            assignment_type=self.project.assignment_types.get(name="Inspection"),
            assigned_date=datetime.datetime(2018, 4, 15),
            description="test description",
            dispatcher=self.dispatcher,
            due_date=datetime.datetime(2018, 4, 22),
            geometry={"x": 123, "y": 456},
            in_progress_date=datetime.datetime(2018, 4, 18),
            location="here",
            notes="Done",
            paused_date=datetime.datetime(2018, 4, 19),
            completed_date=datetime.datetime(2018, 4, 21),
            priority="critical",
            status="completed",
            work_order_id="ID3",
            worker=self.worker
        )

    def add_declined_assignment(self):
        self.project.assignments.add(
            assignment_type=self.project.assignment_types.get(name="Inspection"),
            assigned_date=datetime.datetime(2018, 4, 15),
            description="test description",
            dispatcher=self.dispatcher,
            due_date=datetime.datetime(2018, 4, 22),
            geometry={"x": 123, "y": 456},
            declined_date=datetime.datetime(2018, 4, 18),
            declined_comment="declined",
            location="here",
            notes="Done",
            priority="critical",
            status="declined",
            work_order_id="ID4",
            worker=self.worker
        )

    def add_assignment_types(self):
        # Add an assignment type
        self.project.assignment_types.add(name="Removal")
        self.project.assignment_types.add(name="Inspection")

    def add_dispatcher(self):
        self.project.dispatchers.add(user_id='ar_workforce_python_api2',
                                     contact_number='123-456-7890',
                                     name='ar_workforce_python_api2')

    def add_worker(self):
        self.project.workers.add(user_id='ar_workforce_python_api2', contact_number='123-456-7890', name='ar_workforce_python_api2')

    def reset_project(self):
        self.project.assignments.batch_delete(self.project.assignments.search())
        self.project.assignment_types.batch_delete(self.project.assignment_types.search())
        self.project.workers.batch_delete(self.project.workers.search())
        self.project.dispatchers.batch_delete(self.project.dispatchers.search(where="{} <> '{}'".format(self.project._dispatcher_schema.user_id, 'ar_workforce_python_api')))

    def setup_project(self):
        self.add_assignment_types()
        self.add_worker()
        self.add_dispatcher()
        self.worker = self.project.workers.search()[0]
        self.dispatcher = self.project.dispatchers.get(object_id=1)
        self.add_unassigned_assignment()
        self.add_unassigned_assignment()


    @classmethod
    def setUpClass(cls):
        """
        Check if ArcGIS.com can be reached
        :return:
        """
        _conf_reader = ConfigParser()
        _conf_reader.read(DinoConfigs.portal_list_file, 'UTF-8')

        cls.portal_url = _conf_reader['workforce_ago']['url']
        cls.portal_username = _conf_reader['workforce_ago']['publisher_user']
        cls.portal_password = _conf_reader['workforce_ago']['publisher_password']
        cls.gis = GIS(cls.portal_url, cls.portal_username, cls.portal_password)
        t = datetime.datetime.now()
        cls.time_stamp = str.format("Time stamp: {0}_{1}_{2}_{3}_{4}_{5}", str(t.year),
                                    str(t.month), str(t.day), str(t.hour), str(t.minute), str(t.second))
        cls.project = create_project(cls.time_stamp)


        r1 = PreconditionChecks.can_ping_portal(cls.portal_url)
        if not r1:
            cls.class_skip = True
        print("==================================================================")
        print("Beginning tests in Test_Workforce_AssignmentManager class")

    def setUp(self):
        # reset project for each test
        self.reset_project()
        self.setup_project()
        print("Test: "+self._testMethodName)
        self.namePrefix = "dino_"

        t = datetime.datetime.now()
        self.time_stamp = str.format("Time stamp: {0}_{1}_{2}_{3}_{4}_{5}", str(t.year),
              str(t.month), str(t.day), str(t.hour), str(t.minute), str(t.second))
        print("Time stamp: " + self.time_stamp)

    def tearDown(self):
        print("------------------------------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        try:
            cls.project.delete()
        except Exception as e:
            print("Failed to delete project successfully!")
        print("\n==================================================================")

    def test_search_assignment(self):
        try:
            assignments = self.project.assignments.search("assignmentType=0")
            self.assertEqual(len(assignments), 0, "Incorrect number of assignments")
            assignments = self.project.assignments.search("assignmentType=2")
            self.assertEqual(len(assignments), 2, "Incorrect number of assignments")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_update_assignment(self):
        try:
            assignment = self.project.assignments.search()[0]
            self.assertEqual(assignment.description, "Do some work")
            self.assertEqual(assignment.status, "unassigned")
            self.assertEqual(assignment.worker, None)
            assignment.update(description="Updated",
                              status="assigned",
                              worker=self.worker,
                              assigned_date=datetime.datetime(2018, 4, 17))
            assignment = self.project.assignments.search()[0]
            self.assertEqual(assignment.description, "Updated", "Incorrect description")
            self.assertEqual(assignment.status, "assigned", "Incorrect status")
            self.assertEqual(assignment.worker.id, self.worker.id, "Incorrect worker")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_batch_update_assignment(self):
        try:
            assignments = self.project.assignments.search()
            for assignment in assignments:
                self.assertEqual(assignment.description, "Do some work")
                self.assertEqual(assignment.status, "unassigned")
                self.assertEqual(assignment.worker, None)
                assignment.worker = self.worker
                assignment.status = "assigned"
                assignment.assigned_date = datetime.datetime(2018, 4, 17)
            self.project.assignments.batch_update(assignments)
            assignments = self.project.assignments.search()
            for assignment in assignments:
                self.assertEqual(assignment.status, "assigned", "Incorrect status")
                self.assertEqual(assignment.worker.id, self.worker.id, "Incorrect worker")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_delete_assignment(self):
        try:
            assignments = self.project.assignments.search()
            self.assertEqual(len(assignments), 2, "Incorrect number of assignments")
            assignments[0].delete()
            assignments = self.project.assignments.search()
            self.assertEqual(len(assignments), 1, "Incorrect number of assignments")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_batch_delete_assignment(self):
        try:
            assignments = self.project.assignments.search()
            self.assertEqual(len(assignments), 2, "Incorrect number of assignments")
            self.project.assignments.batch_delete(assignments)
            assignments = self.project.assignments.search()
            self.assertEqual(len(assignments), 0, "Incorrect number of assignments")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_comp_assignment_properties(self):
        try:
            # add the assignment to test
            self.add_completed_assignment()

            assignment = self.project.assignments.search()[-1]
            self.assertEqual(assignment.geometry, {"x": 123, "y": 456}, "Incorrect geometry")
            self.assertEqual(assignment.assignment_type.name, "Inspection", "Incorrect assignment type")
            self.assertEqual(assignment.assigned_date.date(), datetime.datetime(2018, 4, 15).date(), "Incorrect assigned date")
            self.assertEqual(assignment.completed_date.date(), datetime.datetime(2018, 4, 21).date(), "Incorrect completed date")
            self.assertEqual(assignment.declined_comment, None, "Incorrect declined comment")
            self.assertEqual(assignment.declined_date, None, "Incorrect declined date")
            self.assertEqual(assignment.description, "test description", "Incorrect description")
            self.assertEqual(assignment.due_date.date(), datetime.datetime(2018, 4, 22).date(), "Incorrect due date")
            self.assertEqual(assignment.in_progress_date.date(), datetime.datetime(2018, 4, 18).date(), "Incorrect in progress date")
            self.assertEqual(assignment.location, "here", "Incorrect location")
            self.assertEqual(assignment.paused_date.date(), datetime.datetime(2018, 4, 19).date())
            self.assertEqual(assignment.priority, "critical", "Incorrect priority")
            self.assertEqual(assignment.status, "completed", "Incorrect status")
            self.assertEqual(assignment.work_order_id, "ID3", "Incorrect work order id")
            self.assertEqual(assignment.worker.id, self.worker.id, "Incorrect worker id")


        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_decl_assignment_properties2(self):
        try:
            # add the assignment to test
            self.add_declined_assignment()

            assignment = self.project.assignments.search()[-1]
            self.assertEqual(assignment.geometry, {"x": 123, "y": 456}, "Incorrect geometry")
            self.assertEqual(assignment.assignment_type.name, "Inspection", "Incorrect assignment type")
            self.assertEqual(assignment.assigned_date.date(), datetime.datetime(2018, 4, 15).date(),
                             "Incorrect assigned date")
            self.assertEqual(assignment.declined_comment, "declined", "Incorrect declined comment")
            self.assertEqual(assignment.declined_date.date(), datetime.datetime(2018, 4, 18).date(), "Incorrect declined date")
            self.assertEqual(assignment.description, "test description", "Incorrect description")
            self.assertEqual(assignment.dispatcher.id, 1, "Incorrect dispatcher id")
            self.assertEqual(assignment.due_date.date(), datetime.datetime(2018, 4, 22).date(),
                             "Incorrect due date")
            self.assertEqual(assignment.location, "here", "Incorrect location")
            self.assertEqual(assignment.priority, "critical", "Incorrect priority")
            self.assertEqual(assignment.status, "declined", "Incorrect status")
            self.assertEqual(assignment.work_order_id, "ID4", "Incorrect work order id")
            self.assertEqual(assignment.worker.id, self.worker.id, "Incorrect worker id")


        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())


class Test_Workforce_Assignments_No_Assignments(unittest.TestCase):
    """
    Test to verify that assignments can be queried and added when there are no assignments in the project
    """

    def reset_project(self):
        self.project.assignments.batch_delete(self.project.assignments.search())
        self.project.tracks.batch_delete(self.project.tracks.search())

    @classmethod
    def setUpClass(cls):
        """
        Check if ArcGIS.com can be reached
        :return:
        """
        _conf_reader = ConfigParser()
        _conf_reader.read(DinoConfigs.portal_list_file, 'UTF-8')

        cls.portal_url = _conf_reader['workforce_ago']['url']
        cls.portal_username = _conf_reader['workforce_ago']['publisher_user']
        cls.portal_password = _conf_reader['workforce_ago']['publisher_password']
        cls.project_id = "9a03ef9b1ed94ed0a5c798405b81a795"
        cls.gis = GIS(cls.portal_url, cls.portal_username, cls.portal_password)
        cls.project = Project(cls.gis.content.get(cls.project_id))
        cls.dispatcher = cls.project.dispatchers.get(object_id=1)
        cls.worker = cls.project.workers.get(object_id=1)
        cls.inspection = cls.project.assignment_types.get(name="Inspection")
        cls.repair = cls.project.assignment_types.get(name="Repair")

        r1 = PreconditionChecks.can_ping_portal(cls.portal_url)
        if not r1:
            cls.class_skip = True
        print("==================================================================")
        print("Beginning tests in Test_Workforce_AssignmentManager class")

    def setUp(self):
        self.reset_project()
        print("Test: " + self._testMethodName)
        self.namePrefix = "dino_"

        t = datetime.datetime.now()
        self.time_stamp = str.format("Time stamp: {0}_{1}_{2}_{3}_{4}_{5}", str(t.year),
                                     str(t.month), str(t.day), str(t.hour), str(t.minute), str(t.second))
        print("Time stamp: " + self.time_stamp)

    def tearDown(self):
        print("------------------------------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")

    def test_get_empty_assignments(self):
        try:
            assignment = self.project.assignments.get(object_id=0)
            self.assertFalse(assignment)  # no assignments
            assignment = self.project.assignments.get(object_id=1)
            self.assertFalse(assignment)  # no assignments

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_add_assignment1(self):
        try:
            assignment = self.project.assignments.add(
                geometry={"x": 123, "y": 456},
                status="unassigned",
                location="A location",
                description="Do some work",
                dispatcher=self.dispatcher,
                assignment_type=self.inspection
            )
            self.assertIsInstance(assignment, Assignment, "Incorrect Type")
            self.assertEqual(assignment.status, "unassigned")
            self.assertEqual(assignment.location, "A location")
            self.assertEqual(assignment.description, "Do some work")
            self.assertEqual(assignment.geometry, {"x": 123, "y": 456})
            self.assertEqual(assignment.dispatcher.id, self.dispatcher.id)
            # test fetching the new assignment
            downloaded_assignment = self.project.assignments.search()[0]
            self.assertIsInstance(downloaded_assignment, Assignment, "Incorrect Type")
            self.assertEqual(downloaded_assignment.status, "unassigned")
            self.assertEqual(downloaded_assignment.location, "A location")
            self.assertEqual(downloaded_assignment.description, "Do some work")
            self.assertEqual(downloaded_assignment.geometry, {"x": 123, "y": 456})
            self.assertEqual(downloaded_assignment.dispatcher.id, self.dispatcher.id)

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_add_assignment2(self):
        try:
            now = datetime.datetime(2018, 4, 16)
            assignment = self.project.assignments.add(
                geometry={"x": 123, "y": 456},
                status="assigned",
                location="A location",
                description="Do some work",
                dispatcher=self.dispatcher,
                assignment_type=self.inspection,
                worker=self.worker,
                assigned_date=now
            )
            self.assertIsInstance(assignment, Assignment, "Incorrect Type")
            self.assertEqual(assignment.status, "assigned")
            self.assertEqual(assignment.location, "A location")
            self.assertEqual(assignment.description, "Do some work")
            self.assertEqual(assignment.geometry, {"x": 123, "y": 456})
            self.assertEqual(assignment.dispatcher.id, self.dispatcher.id)
            self.assertEqual(assignment.worker.id, self.worker.id)
            self.assertEqual(assignment.assigned_date.date(), now.date())
            # test fetching the new assignment
            downloaded_assignment = self.project.assignments.search()[0]
            self.assertIsInstance(downloaded_assignment, Assignment, "Incorrect Type")
            self.assertEqual(downloaded_assignment.status, "assigned")
            self.assertEqual(downloaded_assignment.location, "A location")
            self.assertEqual(downloaded_assignment.description, "Do some work")
            self.assertEqual(downloaded_assignment.geometry, {"x": 123, "y": 456})
            self.assertEqual(downloaded_assignment.dispatcher.id, self.dispatcher.id)
            self.assertEqual(downloaded_assignment.worker.id, self.worker.id)
            self.assertEqual(downloaded_assignment.assigned_date.date(), now.date())

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_batch_add_assignments(self):
        try:
            now = datetime.datetime(2018, 4, 16)
            assignment = Assignment(
                self.project,
                geometry={"x": 123, "y": 456},
                status="assigned",
                location="A location",
                description="Do some work",
                dispatcher=self.dispatcher,
                assignment_type=self.inspection,
                worker=self.worker,
                assigned_date=now
            )
            assignment2 = Assignment(
                self.project,
                geometry={"x": 123, "y": 456},
                status="unassigned",
                location="A location",
                description="Do some work",
                dispatcher=self.dispatcher,
                assignment_type=self.inspection,
            )
            # add assignment without assigned date
            assignment3 = Assignment(
                self.project,
                geometry={"x": 123, "y": 456},
                status="assigned",
                location="A location",
                description="Do some work",
                dispatcher=self.dispatcher,
                assignment_type=self.inspection,
                worker=self.worker
            )
            assignments = self.project.assignments.batch_add([assignment, assignment2, assignment3])
            # test fetching the new assignment
            downloaded_assignment1 = self.project.assignments.search()[0]
            downloaded_assignment2 = self.project.assignments.search()[1]
            self.assertIsInstance(downloaded_assignment1, Assignment, "Incorrect Type")
            self.assertEqual(downloaded_assignment1.status, "assigned")
            self.assertEqual(downloaded_assignment1.location, "A location")
            self.assertEqual(downloaded_assignment1.description, "Do some work")
            self.assertEqual(downloaded_assignment1.geometry, {"x": 123, "y": 456})
            self.assertEqual(downloaded_assignment1.dispatcher.id, self.dispatcher.id)
            self.assertEqual(downloaded_assignment1.worker.id, self.worker.id)
            self.assertEqual(downloaded_assignment1.assigned_date.date(), now.date())

            self.assertIsInstance(downloaded_assignment2, Assignment, "Incorrect Type")
            self.assertEqual(downloaded_assignment2.status, "unassigned")
            self.assertEqual(downloaded_assignment2.location, "A location")
            self.assertEqual(downloaded_assignment2.description, "Do some work")
            self.assertEqual(downloaded_assignment2.geometry, {"x": 123, "y": 456})
            self.assertEqual(downloaded_assignment2.dispatcher.id, self.dispatcher.id)

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_add_assignment_validation(self):
        try:
            # no assignment type
            with self.assertRaises(ValidationError):
                self.project.assignments.add(
                    geometry={"x": 123, "y": 456},
                    location="here",
                    status="unassigned",
                    description="Do some work",
                    dispatcher=self.dispatcher
                )
            # empty assignment type
            with self.assertRaises(ValidationError):
                self.project.assignments.add(
                    geometry={"x": 123, "y": 456},
                    location="here",
                    status="unassigned",
                    description="Do some work",
                    dispatcher=self.dispatcher,
                    assignment_type=AssignmentType(self.project)
                )
            # worker but not assigned
            with self.assertRaises(ValidationError):
                self.project.assignments.add(
                    geometry={"x": 123, "y": 456},
                    location="here",
                    status="unassigned",
                    description="Do some work",
                    dispatcher=self.dispatcher,
                    worker=self.worker,
                    assignment_type=self.inspection
                )
            # empty worker
            with self.assertRaises(ValidationError):
                self.project.assignments.add(
                    geometry={"x": 123, "y": 456},
                    location="here",
                    status="assigned",
                    description="Do some work",
                    dispatcher=self.dispatcher,
                    worker=Worker(self.project),
                    assignment_type=self.inspection
                )
            # empty dispatcher
            with self.assertRaises(ValidationError):
                self.project.assignments.add(
                    geometry={"x": 123, "y": 456},
                    location="here",
                    status="unassigned",
                    description="Do some work",
                    dispatcher=Dispatcher(self.project),
                    assignment_type=self.inspection
                )
            # no status
            with self.assertRaises(ValidationError):
                self.project.assignments.add(
                    geometry={"x": 123, "y": 456},
                    location="here",
                    description="Do some work",
                    dispatcher=self.dispatcher,
                    assignment_type=self.inspection
                )
            # no geometry
            with self.assertRaises(ValidationError):
                self.project.assignments.add(
                    status="unassigned",
                    description="Do some work",
                    dispatcher=self.dispatcher,
                    location="here",
                    assignment_type=self.inspection
                )
            # no location
            with self.assertRaises(ValidationError):
                self.project.assignments.add(
                    geometry={"x": 123, "y": 456},
                    status="unassigned",
                    description="Do some work",
                    dispatcher=self.dispatcher,
                    assignment_type=self.inspection
                )
            # assigned without worker or date
            with self.assertRaises(ValidationError):
                self.project.assignments.add(
                    geometry={"x": 123, "y": 456},
                    status="assigned",
                    location="A location",
                    description="Do some work",
                    dispatcher=self.dispatcher,
                    assignment_type=self.inspection
                )
            # assigned without worker
            with self.assertRaises(ValidationError):
                self.project.assignments.add(
                    geometry={"x": 123, "y": 456},
                    status="assigned",
                    location="A location",
                    description="Do some work",
                    dispatcher=self.dispatcher,
                    assignment_type=self.inspection,
                    assigned_date=datetime.datetime.now()
                )
            # declined no comment
            with self.assertRaises(ValidationError):
                self.project.assignments.add(
                    geometry={"x": 123, "y": 456},
                    status="declined",
                    location="A location",
                    description="Do some work",
                    dispatcher=self.dispatcher,
                    assignment_type=self.inspection,
                    worker=self.worker,
                    declined_date=datetime.datetime.now()
                )


        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())


#TestModule
def tearDownModule():
    print("**End Workforce AssignmentManager Tests**")