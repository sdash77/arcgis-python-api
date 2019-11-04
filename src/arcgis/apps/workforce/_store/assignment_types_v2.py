""" Defines store functions for working with AssignmentTypes.
"""

from ... import workforce
from .utils import validate, add_features, update_features, remove_features


def get_assignment_type_v2(project, description):
    """ Gets the identified AssignmentType. Exactly one form of identification should be provided.
        :param project:
        :param description: The AssignmentType description.
    """
    assignment_types = get_assignment_types_v2(project)
    return next((at for at in assignment_types if at.description == description), None)


def get_assignment_types_v2(project):
    """ Gets all AssignmentTypes for the project.
        :param project:
        :returns: A list of AssignmentTypes.
    """
    return query_assignment_types(project, '1=1')


def query_assignment_types(project, where='1=1'):
    """ Executes a query against the assignment types table.
        :param project: The project in which to query assignment types.
        :param where: An ArcGIS where clause.
        :returns: list of Assignment Types
    """
    assignment_type_features = project.assignment_types_table.query(where, return_all_freatures=True).features
    return [workforce.AssignmentType(project, feature) for feature in assignment_type_features]


def add_assignment_type_v2(project, description):
    """
    Adds a new assignment type
    """
    assignment_type = workforce.AssignmentType(project, description)
    return add_assignment_types_v2(project, [assignment_type])[0]


def add_assignment_types_v2(project, assignment_types):
    """ Adds an AssignmentType to a project.

        Side effect: Each AssignmentType in assignment_types will be assigned a unique code.

        :param project:
        :param assignment_types: list of AssignmentTypes
        :raises ValidationError: Indicates that one or more assignment types failed validation.
    """
    use_global_ids = True
    for assignment_type in assignment_types:
        assignment_type.project = project
        validate(assignment_type)
        if assignment_type.global_id is None:
            use_global_ids = False

    features = [assignment_type.feature for assignment_type in assignment_types]
    add_features(project.assignments_type_table, features, use_global_ids)
    return assignment_types


def update_assignment_types_v2(project, assignment_types):
    """ Updates the AssignmentTypes.
        :param project:
        :param assignment_types: list of AssignmentTypes
        :raises ValidationError: Indicates that one or more assignment types failed validation.
    """
    project._update_cached_objects()
    for assignment_type in assignment_types:
        validate(assignment_type._validate_for_update)
    features = [assignment_type.feature for assignment_type in assignment_types]
    update_features(project.assignments_type_table, features)
    return assignment_types


def update_assignment_type_v2(project, assignment_type, description=None):
    """Updates an assignment types description"""
    if description:
        assignment_type.description = description
    return update_assignment_types_v2(project, [assignment_type])[0]


def delete_assignment_types_v2(project, assignment_types):
    """ Removes AssignmentTypes from the project.
        :param project:
        :param assignment_types: list of AssignmentTypes.
    """
    project._update_cached_objects()
    for assignment_type in assignment_types:
        validate(assignment_type._validate_for_remove)
    features = [assignment_type.feature for assignment_type in assignment_types]
    remove_features(project.assignment_types_table, features)
