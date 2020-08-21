import connexion
import six

from swagger_server.models.project_long import ProjectLong  # noqa: E501
from swagger_server.models.project_short import ProjectShort  # noqa: E501
from swagger_server import util
from swagger_server.response_code import projects_controller as rc


def projects_add_members_put(project_id, project_members=None):  # noqa: E501
    """add members to an existing project

    add members to an existing project # noqa: E501

    :param project_id: 
    :type project_id: str
    :param project_members: 
    :type project_members: List[str]

    :rtype: ProjectLong
    """
    return rc.projects_add_members_put(project_id, project_members=None)


def projects_add_owners_put(project_id, project_owners=None):  # noqa: E501
    """add owners to an existing project

    add owners to an existing project # noqa: E501

    :param project_id: 
    :type project_id: str
    :param project_owners: 
    :type project_owners: List[str]

    :rtype: ProjectLong
    """
    return rc.projects_add_owners_put(project_id, project_owners=None)


def projects_add_tags_put(project_id, tags=None):  # noqa: E501
    """add tags to an existing project

    add tags to an existing project # noqa: E501

    :param project_id: 
    :type project_id: str
    :param tags: 
    :type tags: List[str]

    :rtype: ProjectLong
    """
    return rc.projects_add_tags_put(project_id, tags=None)


def projects_create_post(name, description, facility=None, tags=None, project_owners=None, project_members=None):  # noqa: E501
    """create new project

    create new project # noqa: E501

    :param name: 
    :type name: str
    :param description: 
    :type description: str
    :param facility: 
    :type facility: str
    :param tags: 
    :type tags: List[str]
    :param project_owners: 
    :type project_owners: List[str]
    :param project_members: 
    :type project_members: List[str]

    :rtype: ProjectLong
    """
    return rc.projects_create_post(name, description, facility=None, tags=None, project_owners=None, project_members=None)


def projects_delete_delete(project_id):  # noqa: E501
    """delete existing project

    delete existing project # noqa: E501

    :param project_id: Project identifier as UUID
    :type project_id: str

    :rtype: None
    """
    return rc.projects_delete_delete(project_id)


def projects_get():  # noqa: E501
    """list of projects

    list of projects # noqa: E501


    :rtype: ProjectShort
    """
    return rc.projects_get()


def projects_project_idget(project_id):  # noqa: E501
    """project details

    project details # noqa: E501

    :param project_id: Project identifier as UUID
    :type project_id: str

    :rtype: ProjectLong
    """
    return rc.projects_project_idget(project_id)


def projects_remove_members_put(project_id, project_members=None):  # noqa: E501
    """remove members to an existing project

    remove members to an existing project # noqa: E501

    :param project_id: 
    :type project_id: str
    :param project_members: 
    :type project_members: List[str]

    :rtype: ProjectLong
    """
    return rc.projects_remove_members_put(project_id, project_members=None)


def projects_remove_owners_put(project_id, project_owners=None):  # noqa: E501
    """remove owners to an existing project

    remove owners to an existing project # noqa: E501

    :param project_id: 
    :type project_id: str
    :param project_owners: 
    :type project_owners: List[str]

    :rtype: ProjectLong
    """
    return rc.projects_remove_owners_put(project_id, project_owners=None)


def projects_remove_tags_put(project_id, tags=None):  # noqa: E501
    """remove tags to an existing project

    remove tags to an existing project # noqa: E501

    :param project_id: 
    :type project_id: str
    :param tags: 
    :type tags: List[str]

    :rtype: ProjectLong
    """
    return rc.projects_remove_tags_put(project_id, tags=None)


def projects_update_put(project_id, name=None, description=None, facility=None):  # noqa: E501
    """update an existing project

    update an existing project name, description or facility # noqa: E501

    :param project_id: 
    :type project_id: str
    :param name: 
    :type name: str
    :param description: 
    :type description: str
    :param facility: 
    :type facility: str

    :rtype: ProjectLong
    """
    return rc.projects_update_put(project_id, name=None, description=None, facility=None)
