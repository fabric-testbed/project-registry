import os

from flask import request

from swagger_server.db_models import FabricProjects
from swagger_server.models.project_long import ProjectLong  # noqa: E501
from swagger_server.models.project_short import ProjectShort  # noqa: E501
from .authorization_controller import get_api_user, cors_401, cors_response
from .local_controller import get_project_long_by_uuid, add_tags_by_project_uuid, remove_tags_by_project_uuid, \
    update_project_by_project_uuid, add_members_by_project_uuid, get_project_short_by_uuid, \
    add_owners_by_project_uuid, remove_members_by_project_uuid, remove_owners_by_project_uuid, project_create, \
    project_delete
from swagger_server.response_code import PROJECTS_TAGS


def projects_add_members_put(uuid, project_members=None):  # noqa: E501
    """add members to an existing project

    Add members to an existing project # noqa: E501

    :param uuid:
    :type uuid: str
    :param project_members: Array of project members as UUID
    :type project_members: List[str]

    :rtype: ProjectLong
    """
    api_user = get_api_user(api_request=request)
    if not api_user.uuid:
        return cors_401()

    user_is_creator = next((s for s in api_user.roles if uuid + '-pc' in s), None)
    user_is_owner = next((s for s in api_user.roles if uuid + '-po' in s), None)

    # ALLOW: project_creator, project_owner, facility-operator
    if not user_is_creator and not user_is_owner and not os.getenv('ROLE_FACILITY_OPERATORS') in api_user.roles:
        return cors_401()

    fab_project = FabricProjects.query.filter_by(uuid=uuid).one_or_none()
    if fab_project:
        add_members_by_project_uuid(project_uuid=uuid, project_members=project_members)
    else:
        return cors_response(
            request=request,
            status_code=404,
            body='Project UUID reference Not Found: {0}'.format(str(uuid)),
            x_error='Not Found'
        )

    return get_project_long_by_uuid(uuid)


def projects_add_owners_put(uuid, project_owners=None):  # noqa: E501
    """add owners to an existing project

    Add owners to an existing project # noqa: E501

    :param uuid:
    :type uuid: str
    :param project_owners: Array of project owners as UUID
    :type project_owners: List[str]

    :rtype: ProjectLong
    """
    api_user = get_api_user(api_request=request)
    if not api_user.uuid:
        return cors_401()

    user_is_creator = next((s for s in api_user.roles if uuid + '-pc' in s), None)

    # ALLOW: project_creator, facility-operator
    if not user_is_creator and not os.getenv('ROLE_FACILITY_OPERATORS') in api_user.roles:
        return cors_401()

    fab_project = FabricProjects.query.filter_by(uuid=uuid).one_or_none()
    if fab_project:
        add_owners_by_project_uuid(project_uuid=uuid, project_owners=project_owners)
    else:
        return cors_response(
            request=request,
            status_code=404,
            body='Project UUID reference Not Found: {0}'.format(str(uuid)),
            x_error='Not Found'
        )

    return get_project_long_by_uuid(uuid)


def projects_add_tags_put(uuid, tags=None):  # noqa: E501
    """add tags to an existing project

    Add tags to an existing project # noqa: E501

    :param uuid:
    :type uuid: str
    :param tags: 
    :type tags: List[str]

    :rtype: ProjectLong
    """
    api_user = get_api_user(api_request=request)
    if not api_user.uuid:
        return cors_401()

    # ALLOW: facility-operators
    if os.getenv('ROLE_FACILITY_OPERATORS') not in api_user.roles:
        return cors_401()

    if tags:
        fab_project = FabricProjects.query.filter_by(uuid=uuid).one_or_none()
        if fab_project:
            for tag in tags:
                if tag not in PROJECTS_TAGS.options:
                    return cors_response(
                        request=request,
                        status_code=400,
                        body="Attempting to add invalid tag '{0}'".format(tag),
                        x_error='Bad Request'
                    )
            add_tags_by_project_uuid(project_uuid=uuid, tags=tags)
        else:
            return cors_response(
                request=request,
                status_code=404,
                body='Project UUID reference Not Found: {0}'.format(str(uuid)),
                x_error='Not Found'
            )

    return get_project_long_by_uuid(uuid)


def projects_create_post(name, description, facility, tags=None, project_owners=None,
                         project_members=None):  # noqa: E501
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
    :param project_owners: Array of project owners as UUID
    :type project_owners: List[str]
    :param project_members: Array of project members as UUID
    :type project_members: List[str]

    :rtype: ProjectLong
    """
    api_user = get_api_user(api_request=request)
    if not api_user.uuid:
        return cors_401()

    # ALLOW: project-leads or facility-operators
    if not os.getenv('ROLE_PROJECT_LEADS') in api_user.roles \
            and not os.getenv('ROLE_FACILITY_OPERATORS') in api_user.roles:
        return cors_401()

    # ALLOW: facility-operators to add tags
    if tags and not os.getenv('ROLE_FACILITY_OPERATORS') in api_user.roles:
        return cors_response(
            request=request,
            status_code=401,
            body='Unauthorized',
            x_error='Authentication required'
        )

    project_creator = api_user.uuid
    project_uuid = project_create(name=name, description=description, facility=facility, tags=tags,
                                  project_creator=project_creator, project_owners=project_owners,
                                  project_members=project_members)

    return get_project_long_by_uuid(project_uuid)


def projects_delete_delete(uuid):  # noqa: E501
    """delete existing project

    Delete existing project # noqa: E501

    :param uuid: Project identifier as UUID
    :type uuid: str

    :rtype: None
    """
    api_user = get_api_user(api_request=request)
    if not api_user.uuid:
        return cors_401()

    user_is_creator = next((s for s in api_user.roles if uuid + '-pc' in s), None)

    # ALLOW: project_creator, facility-operator
    if not user_is_creator and not os.getenv('ROLE_FACILITY_OPERATORS') in api_user.roles:
        return cors_401()

    fab_project = FabricProjects.query.filter_by(uuid=uuid).one_or_none()
    if fab_project:
        project_delete(project_uuid=uuid)
    else:
        return cors_response(
            request=request,
            status_code=404,
            body='Project UUID reference Not Found: {0}'.format(str(uuid)),
            x_error='Not Found'
        )

    return 'OK'


def projects_get(project_name=None):  # noqa: E501
    """list of projects

    List of projects # noqa: E501

    :param project_name: Search Project by Name (ILIKE)
    :type project_name: str

    :rtype: ProjectShort
    """
    api_user = get_api_user(api_request=request)
    if not api_user.uuid:
        return cors_401()

    # ALLOW: fabric-active-users
    if not os.getenv('ROLE_ACTIVE_USERS') in api_user.roles:
        return cors_401()

    fab_projects = []
    if project_name:
        projects = FabricProjects.query.filter(
            FabricProjects.name.ilike("%" + project_name + "%")
        ).order_by(FabricProjects.name).all()
    else:
        projects = FabricProjects.query.order_by(FabricProjects.name).all()
    for project in projects:
        fab_projects.append(get_project_short_by_uuid(project_uuid=project.__asdict__().get('uuid')))
    response = fab_projects

    return response


def projects_tags_get(search=None):  # noqa: E501
    """List of valid Project Tags

    List of valid Project Tags # noqa: E501

    :param search: search term applied
    :type search: str

    :rtype: List[str]
    """
    if search:
        response = [tag for tag in PROJECTS_TAGS.options if search.casefold() in tag.casefold()]
    else:
        response = PROJECTS_TAGS.options

    return response


def projects_remove_members_put(uuid, project_members=None):  # noqa: E501
    """remove members to an existing project

    Remove members to an existing project # noqa: E501

    :param uuid:
    :type uuid: str
    :param project_members: Array of project members as UUID
    :type project_members: List[str]

    :rtype: ProjectLong
    """
    api_user = get_api_user(api_request=request)
    if not api_user.uuid:
        return cors_401()

    user_is_creator = next((s for s in api_user.roles if uuid + '-pc' in s), None)
    user_is_owner = next((s for s in api_user.roles if uuid + '-po' in s), None)

    # ALLOW: project_creator, project_owner, facility-operator
    if not user_is_creator and not user_is_owner and not os.getenv('ROLE_FACILITY_OPERATORS') in api_user.roles:
        return cors_401()

    fab_project = FabricProjects.query.filter_by(uuid=uuid).one_or_none()
    if fab_project:
        remove_members_by_project_uuid(project_uuid=uuid, project_members=project_members)
    else:
        return cors_response(
            request=request,
            status_code=404,
            body='Project UUID reference Not Found: {0}'.format(str(uuid)),
            x_error='Not Found'
        )

    return get_project_long_by_uuid(uuid)


def projects_remove_owners_put(uuid, project_owners=None):  # noqa: E501
    """remove owners to an existing project

    Remove owners to an existing project # noqa: E501

    :param uuid:
    :type uuid: str
    :param project_owners: Array of project owners as UUID
    :type project_owners: List[str]

    :rtype: ProjectLong
    """
    api_user = get_api_user(api_request=request)
    if not api_user.uuid:
        return cors_401()

    user_is_creator = next((s for s in api_user.roles if uuid + '-pc' in s), None)

    # ALLOW: project_creator, facility-operator
    if not user_is_creator and not os.getenv('ROLE_FACILITY_OPERATORS') in api_user.roles:
        return cors_401()

    fab_project = FabricProjects.query.filter_by(uuid=uuid).one_or_none()
    if fab_project:
        remove_owners_by_project_uuid(project_uuid=uuid, project_owners=project_owners)
    else:
        return cors_response(
            request=request,
            status_code=404,
            body='Project UUID reference Not Found: {0}'.format(str(uuid)),
            x_error='Not Found'
        )

    return get_project_long_by_uuid(uuid)


def projects_remove_tags_put(uuid, tags=None):  # noqa: E501
    """remove tags to an existing project

    Remove tags to an existing project # noqa: E501

    :param uuid:
    :type uuid: str
    :param tags: 
    :type tags: List[str]

    :rtype: ProjectLong
    """
    api_user = get_api_user(api_request=request)
    if not api_user.uuid:
        return cors_401()

    # ALLOW: facility-operators
    if os.getenv('ROLE_FACILITY_OPERATORS') not in api_user.roles:
        return cors_401()

    if tags:
        fab_project = FabricProjects.query.filter_by(uuid=uuid).one_or_none()
        if fab_project:
            remove_tags_by_project_uuid(project_uuid=uuid, tags=tags)
        else:
            return cors_response(
                request=request,
                status_code=404,
                body='Project UUID reference Not Found: {0}'.format(str(uuid)),
                x_error='Not Found'
            )

    return get_project_long_by_uuid(uuid)


def projects_update_put(uuid, name=None, description=None, facility=None):  # noqa: E501
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

    :rtype: ProjectLong
    """
    api_user = get_api_user(api_request=request)
    if not api_user.uuid:
        return cors_401()

    user_is_creator = next((s for s in api_user.roles if uuid + '-pc' in s), None)
    user_is_owner = next((s for s in api_user.roles if uuid + '-po' in s), None)

    # ALLOW: project_creator, project_owner, facility-operator
    if not user_is_creator and not user_is_owner and not os.getenv('ROLE_FACILITY_OPERATORS') in api_user.roles:
        return cors_401()

    fab_project = FabricProjects.query.filter_by(uuid=uuid).one_or_none()
    if fab_project:
        update_project_by_project_uuid(project_uuid=uuid, name=name, description=description, facility=facility)
    else:
        return cors_response(
            request=request,
            status_code=404,
            body='Project UUID reference Not Found: {0}'.format(str(uuid)),
            x_error='Not Found'
        )

    return get_project_long_by_uuid(uuid)


def projects_uuid_get(uuid):  # noqa: E501
    """project details

    Project details # noqa: E501

    :param uuid: Project identifier as UUID
    :type uuid: str

    :rtype: ProjectLong
    """
    api_user = get_api_user(api_request=request)
    if not api_user.uuid:
        return cors_401()

    # ALLOW: fabric-active-users
    if not os.getenv('ROLE_ACTIVE_USERS') in api_user.roles:
        return cors_401()

    # ALLOW: ProjectLong for user in project or facility-operators, else ProjectShort
    project = FabricProjects.query.filter_by(uuid=uuid).one_or_none()
    if project:
        user_in_project = next((s for s in api_user.roles if uuid in s), None)
        if user_in_project or os.getenv('ROLE_FACILITY_OPERATORS') in api_user.roles:
            pl = get_project_long_by_uuid(uuid)
        else:
            pl = get_project_short_by_uuid(uuid)
    else:
        return cors_response(
            request=request,
            status_code=404,
            body='UUID Not Found: {0}'.format(uuid),
            x_error='Not Found'
        )
    response = pl

    return response
