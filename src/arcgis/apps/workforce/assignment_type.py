"""
Defines the AssignmentType class.
"""
from src.arcgis.apps.workforce._store.assignment_types_v2 import update_assignment_type_v2, delete_assignment_types_v2
from .exceptions import ValidationError, WorkforceWarning
from .model import Model
from .feature_model import FeatureModel
from ._store import *
from warnings import warn
from ._schemas import AssignmentTypesSchema


class AssignmentType(Model):
    """
    Defines the acceptable values for :class:`~arcgis.apps.workforce.Assignment` types.

    ==================     ====================================================================
    **Argument**           **Description**
    ------------------     --------------------------------------------------------------------
    project                Required :class:`~arcgis.apps.workforce.Project`. The project that
                           this assignment belongs to.
    ------------------     --------------------------------------------------------------------
    coded_value            Optional :class:`dict`. The dictionary storing the code and
                           name of the type. Version 1 Project Only.
    ------------------     --------------------------------------------------------------------
    name                   Optional :class:`String`. The name of the assignment type. Version 1
                           Project only
    ==================     ====================================================================

    """

    def __init__(self, project, feature=None, coded_value=None, name=None, description=None):
        self.project = project
        super().__init__()
        if int(self.project.version.split(".")[0]) >= 2:
            if not feature:
                self.description = description
                self._schema = AssignmentTypesSchema(project.assignment_types_table)
        elif coded_value:
            self._coded_value = coded_value
        else:
            self._coded_value = {'code': None, 'name': name}

    def __str__(self):
        if int(self.project.version.split(".")[0]) >= 2:
            return self.description
        else:
            return self.name

    def __repr__(self):
        if int(self.project.version.split(".")[0]) >= 2:
            return "<AssignmentType {}>".format(self.description)
        else:
            return "<AssignmentType {}>".format(self.code)

    def update(self, name=None, description=None):
        """
            Updates the assignment type on the server

            ==================     ====================================================================
            **Argument**           **Description**
            ------------------     --------------------------------------------------------------------
            name                   Optional :class:`String`.
                                   The name of the assignment type
            ------------------     --------------------------------------------------------------------
            description            Optional :class:`String`.
                                   The description of the assignment type
            ==================     ====================================================================
        """
        if int(self.project.version.split(".")[0]) >= 2:
            update_assignment_type_v2(self.project, self, description)
        else:
            update_assignment_type(self.project, self, name)

    def delete(self):
        """Deletes the assignment type from the server"""
        if int(self.project.version.split(".")[0]) >= 2:
            delete_assignment_types_v2(self.project, [self])
        else:
            delete_assignment_types(self.project, [self])

    @property
    def id(self):
        """Gets the id of the assignment type"""
        if int(self.project.version.split(".")[0]) < 2:
            return self.code
        else:
            warn("This is a Version 2 Workforce Project", WorkforceWarning)

    @property
    def code(self):
        """Gets the internal code that uniquely identifies the assignment type"""
        if int(self.project.version.split(".")[0]) < 2:
            return self._coded_value['code']
        else:
            warn("This is a Version 2 Workforce Project", WorkforceWarning)

    @property
    def name(self):
        """Gets/Sets The name of the assignment type"""
        if int(self.project.version.split(".")[0]) < 2:
            return self.name
        else:
            warn("This is a Version 2 Workforce Project", WorkforceWarning)

    @name.setter
    def name(self, value):
        if int(self.project.version.split(".")[0]) < 2:
            self._coded_value['name'] = value
        else:
            warn("This is a Version 2 Workforce Project", WorkforceWarning)

    @property
    def description(self):
        """Gets the name of the assignment type"""
        if int(self.project.version.split(".")[0]) >= 2:
            return self.description
        else:
            warn("This is a Version 1 Workforce Project", WorkforceWarning)

    @description.setter
    def description(self, value):
        if int(self.project.version.split(".")[0]) >= 2:
            self.description = value
        else:
            warn("This is a Version 1 Workforce Project", WorkforceWarning)

    @property
    def coded_value(self):
        """Gets the coded value"""
        return self._coded_value

    def _validate(self, **kwargs):
        errors = super()._validate(**kwargs)
        if int(self.project.version.split(".")[0]) < 2:
            errors += self._validate_name()
            errors += self._validate_name_uniqueness(**kwargs)
        else:
            errors += self._validate_description()
            errors += self._validate_description_uniqueness(**kwargs)
        return errors

    def _validate_for_update(self, **kwargs):
        if int(self.project.version.split(".")[0]) < 2:
            return super()._validate_for_update(**kwargs) + self._validate_code()
        else:
            return super()._validate_for_update(**kwargs)

    def _validate_for_remove(self, **kwargs):
        assignments = kwargs['assignments']
        if int(self.project.version.split(".")[0]) < 2:
            errors = super()._validate_for_remove(**kwargs) + self._validate_code()
            if assignments is None:
                schema = self.project._assignment_schema
                where = "{}={}".format(schema.assignment_type, self.code)
                assignments = self.project.assignments.search(where=where)
            else:
                assignments = [a for a in assignments if a.assignment_type.code == self.code]
        else:
            errors = super()._validate_for_remove(**kwargs)
            assignments = [a for a in assignments if a.assignment_type.description == self.description]

        if assignments:
            errors.append(ValidationError("Cannot remove an in-use AssignmentType", self))
        return errors

    def _validate_name(self):
        errors = []
        if self.name is None or self.name.isspace():
            errors.append(ValidationError("AssignmentType must have a name", self))
        elif '>' in self.name or '<' in self.name or '%' in self.name:
            errors.append(ValidationError("AssignmentType name contains invalid characters", self))
        return errors

    def _validate_name_uniqueness(self, assignment_types=None):
        errors = []
        if assignment_types is None:
            assignment_types = self.project.assignment_types.search()
        for assignment_type in assignment_types:
            if (assignment_type.name == self.name and assignment_type.code != self.code):
                errors.append(ValidationError("AssignmentType name must be unique", self))
        return errors

    def _validate_description(self):
        errors = []
        if self.description is None or self.description.isspace():
            errors.append(ValidationError("AssignmentType must have a name", self))
        elif '>' in self.description or '<' in self.description or '%' in self.description:
            errors.append(ValidationError("AssignmentType name contains invalid characters", self))
        return errors

    def _validate_description_uniqueness(self, assignment_types=None):
        errors = []
        if assignment_types is None:
            assignment_types = self.project.assignment_types.search()
        for assignment_type in assignment_types:
            if (assignment_type.description == self.description):
                errors.append(ValidationError("AssignmentType description must be unique", self))
        return errors

    def _validate_code(self):
        errors = []
        if not isinstance(self.code, int):
            errors.append(ValidationError("Code must be a unique integer", self))
        return errors
