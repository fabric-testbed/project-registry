import connexion
import six

from swagger_server.models.permission import Permission  # noqa: E501
from swagger_server.models.project_long import ProjectLong  # noqa: E501
from swagger_server.models.project_short import ProjectShort  # noqa: E501
from swagger_server import util
from swagger_server.response_code import projects_controller as rc


def projects_add_members_put(uuid, project_members=None):  # noqa: E501
    """add members to an existing project

    Add members to an existing project # noqa: E501

    :param uuid: 
    :type uuid: str
    :param project_members: Array of project members as UUID
    :type project_members: List[str]

    :rtype: ProjectLong
    """
    return rc.projects_add_members_put(uuid, project_members)


def projects_add_owners_put(uuid, project_owners=None):  # noqa: E501
    """add owners to an existing project

    Add owners to an existing project # noqa: E501

    :param uuid: 
    :type uuid: str
    :param project_owners: Array of project owners as UUID
    :type project_owners: List[str]

    :rtype: ProjectLong
    """
    return rc.projects_add_owners_put(uuid, project_owners)


def projects_add_tags_put(uuid, tags=None):  # noqa: E501
    """add tags to an existing project

    Add tags to an existing project # noqa: E501

    :param uuid: 
    :type uuid: str
    :param tags: 
    :type tags: List[str]

    :rtype: ProjectLong
    """
    return rc.projects_add_tags_put(uuid, tags)


def projects_create_post(name, description, facility, tags=None, permissions=None, project_owners=None, project_members=None):  # noqa: E501
    """create new project

    Create new project # noqa: E501

    :param name: 
    :type name: str
    :param description: 
    :type description: str
    :param facility: 
    :type facility: str
    :param tags: 
    :type tags: List[str]
    :param permissions: 
    :type permissions: dict | bytes
    :param project_owners: Array of project owners as UUID
    :type project_owners: List[str]
    :param project_members: Array of project members as UUID
    :type project_members: List[str]

    :rtype: ProjectLong
    """
    if connexion.request.is_json:
        permissions = request.from_dict(connexion.request.get_json())  # noqa: E501
    return rc.projects_create_post(name, description, facility, tags, permissions, project_owners, project_members)


def projects_delete_delete(uuid):  # noqa: E501
    """delete existing project

    Delete existing project # noqa: E501

    :param uuid: Project identifier as UUID
    :type uuid: str

    :rtype: None
    """
    return rc.projects_delete_delete(uuid)


def projects_get(project_name=None):  # noqa: E501
    """list of projects

    List of projects # noqa: E501

    :param project_name: Search Project by Name (ILIKE)
    :type project_name: str

    :rtype: ProjectShort
    """
    return rc.projects_get(project_name)


def projects_remove_members_put(uuid, project_members=None):  # noqa: E501
    """remove members to an existing project

    Remove members to an existing project # noqa: E501

    :param uuid: 
    :type uuid: str
    :param project_members: Array of project members as UUID
    :type project_members: List[str]

    :rtype: ProjectLong
    """
    return rc.projects_remove_members_put(uuid, project_members)


def projects_remove_owners_put(uuid, project_owners=None):  # noqa: E501
    """remove owners to an existing project

    Remove owners to an existing project # noqa: E501

    :param uuid: 
    :type uuid: str
    :param project_owners: Array of project owners as UUID
    :type project_owners: List[str]

    :rtype: ProjectLong
    """
    return rc.projects_remove_owners_put(uuid, project_owners)


def projects_remove_tags_put(uuid, tags=None):  # noqa: E501
    """remove tags to an existing project

    Remove tags to an existing project # noqa: E501

    :param uuid: 
    :type uuid: str
    :param tags: 
    :type tags: List[str]

    :rtype: ProjectLong
    """
    return rc.projects_remove_tags_put(uuid, tags)


def projects_update_put(uuid, name=None, description=None, facility=None, permissions=None):  # noqa: E501
    """update an existing project

    Update an existing project name, description or facility # noqa: E501

    :param uuid: 
    :type uuid: str
    :param name: 
    :type name: str
    :param description: 
    :type description: str
    :param facility: 
    :type facility: str
    :param permissions: 
    :type permissions: dict | bytes

    :rtype: ProjectLong
    """
    if connexion.request.is_json:
        permissions = request.from_dict(connexion.request.get_json())  # noqa: E501
    return rc.projects_update_put(uuid, name, description, facility, permissions)


def projects_uuid_get(uuid):  # noqa: E501
    """project details

    Project details # noqa: E501

    :param uuid: Project identifier as UUID
    :type uuid: str

    :rtype: ProjectLong
    """
    return rc.projects_uuid_get(uuid)
