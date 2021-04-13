from configparser import ConfigParser
from datetime import datetime
from uuid import uuid4

import psycopg2
from flask import request
from pytz import timezone
from swagger_server.models.project_long import ProjectLong  # noqa: E501
from swagger_server.models.project_short import ProjectShort  # noqa: E501

from . import DEFAULT_USER_UUID, DEFAULT_USER_NAME, DEFAULT_USER_EMAIL
from .people_controller import people_uuid_get
from .utils import dict_from_query, run_sql_commands, resolve_empty_people_uuid, \
    filter_out_preexisting_project_owners, filter_out_preexisting_project_members, \
    filter_out_nonexisting_project_owners, filter_out_nonexisting_project_members, \
    validate_project_reference, validate_project_members_list, validate_person_reference, \
    cors_response
from ..authorization.people import get_api_person
from ..authorization.projects import filter_projects_get, authorize_projects_add_members_put, \
    authorize_projects_add_owners_put, authorize_projects_add_tags_put, authorize_projects_create_post, \
    authorize_projects_delete_delete, authorize_projects_get, authorize_projects_remove_members_put, \
    authorize_projects_remove_owners_put, authorize_projects_remove_tags_put, authorize_projects_update_put, \
    authorize_projects_uuid_get, DEFAULT_USER_UUID
from ..comanage_api.comanage_api import comanage_projects_add_members_put, comanage_projects_add_owners_put, \
    comanage_projects_remove_members_put, comanage_projects_remove_owners_put, comanage_projects_create_post, \
    comanage_projects_add_creator_put, comanage_projects_delete_delete, comanage_projects_remove_creators, \
    comanage_check_for_new_users

config = ConfigParser()
config.read('swagger_server/config/config.ini')


def projects_add_members_put(uuid, project_members=None):  # noqa: E501
    """add members to an existing project

    Add members to an existing project # noqa: E501

    :param uuid:
    :type uuid: str
    :param project_members: Array of project members as UUID
    :type project_members: List[str]

    :rtype: ProjectLong
    """
    # validate project reference as provided by uuid
    project_id, project_name, created_by = validate_project_reference(uuid)
    if project_id == -1:
        return cors_response(
            request=request,
            status_code=400,
            body='Project UUID reference Not Found: {0}'.format(str(uuid)),
            x_error='Project UUID Unknown'
        )

    # validate authorization of user making request
    if not authorize_projects_add_members_put(request.headers, uuid, created_by):
        return cors_response(
            request=request,
            status_code=401,
            body='Authorization required for: /projects/add_members',
            x_error='Authorization is missing or invalid'
        )

    # check for new comanage users
    if not comanage_check_for_new_users():
        return cors_response(
            request=request,
            status_code=500,
            body='COmanage Error - Unable to retrieve co_people data',
            x_error='Unable to retrieve co_people data'
        )

    # attempt to resolve any missing people uuids
    resolve_empty_people_uuid()

    # validate new members reference as provided by project_members
    if project_members:
        project_members_new, project_members_unknown = validate_project_members_list(project_members, project_id)
        if project_members_unknown:
            return cors_response(
                request=request,
                status_code=400,
                body = 'Project member UUID reference Not Found: {0}'.format(', '.join(project_members_unknown)),
                x_error = 'Project member UUID Unknown'
            )
    else:
        project_members_new = []

    # add new project members to comanage group
    sql_list = []
    if project_members_new:
        if not comanage_projects_add_members_put(uuid, project_members_new):
            return cors_response(
                request=request,
                status_code=500,
                body='Unable to add members: {0}'.format(str(uuid)),
                x_error='Unable to add members in COmanage'
            )

        # get role_name and cou_id for -pm
        role_name_pm = str(uuid) + '-pm'
        sql = """
        SELECT id from comanage_cous WHERE name = '{0}';
        """.format(role_name_pm)
        try:
            cou_id_pm = dict_from_query(sql)[0].get('id')
        except KeyError or IndexError as err:
            print(err)
            return cors_response(
                request=request,
                status_code=500,
                body='Unable to add members: {0}'.format(str(uuid)),
                x_error='Unable to add members in COmanage'
            )

        # add new members to database
        for person_uuid in project_members_new:
            if person_uuid != DEFAULT_USER_UUID or config.getboolean('mock', 'data'):
                try:
                    # get people id
                    sql = """
                    SELECT id from fabric_people WHERE uuid = '{0}';
                    """.format(person_uuid)
                    dfq = dict_from_query(sql)
                    try:
                        people_id = dfq[0].get('id')
                    except IndexError or KeyError or TypeError as err:
                        print(err)
                        return cors_response(
                            request=request,
                            status_code=404,
                            body='Person UUID Not Found: {0}'.format(str(person_uuid)),
                            x_error='Person UUID Not Found'
                        )

                    # add to project_members table
                    sql = """
                    INSERT INTO project_members(projects_id, people_id)
                    VALUES ({0}, '{1}')
                    ON CONFLICT ON CONSTRAINT project_members_duplicate
                    DO NOTHING
                    """.format(project_id, people_id)
                    sql_list.append(sql)

                except (Exception, psycopg2.DatabaseError) as error:
                    print(error)

    # add new project members to database
    commands = tuple(i for i in sql_list)
    print("[INFO] attempt to add project members data")
    run_sql_commands(commands)

    return projects_uuid_get(uuid)


def projects_add_owners_put(uuid, project_owners=None):  # noqa: E501
    """add owners to an existing project

    Add owners to an existing project # noqa: E501

    :param uuid:
    :type uuid: str
    :param project_owners: Array of project owners as UUID
    :type project_owners: List[str]

    :rtype: ProjectLong
    """
    # validate project reference as provided by uuid
    project_id, project_name, created_by = validate_project_reference(uuid)
    if project_id == -1:
        return cors_response(
            request=request,
            status_code=400,
            body='Project UUID reference Not Found: {0}'.format(str(uuid)),
            x_error='Project UUID Unknown'
        )

    # check authorization
    if not authorize_projects_add_owners_put(request.headers, created_by):
        return cors_response(
            request=request,
            status_code=401,
            body='Authorization information is missing or invalid: /projects/add_owners',
            x_error='Authorization information is missing or invalid'
        )

    # check for new comanage users
    if not comanage_check_for_new_users():
        return cors_response(
            request=request,
            status_code=500,
            body='COmanage Error - Unable to retrieve co_people data',
            x_error='Unable to retrieve co_people data'
        )

    # resolve any missing people uuids
    resolve_empty_people_uuid()

    # validate new owners reference as provided by project_members
    if project_owners:
        project_owners_new, project_owners_unknown = validate_project_members_list(project_owners, project_id)
        if project_owners_unknown:
            return cors_response(
                request=request,
                status_code=400,
                body='Project owner UUID reference Not Found: {0}'.format(', '.join(project_owners_unknown)),
                x_error='Project owner UUID Unknown'
            )
    else:
        project_owners_new = []

    sql_list = []
    if project_owners_new:
        # copy project_members from project_owners_new
        project_members = project_owners_new.copy()

        # validate new members reference as provided by project_members
        if project_members:
            project_members_new, project_members_unknown = validate_project_members_list(project_members, project_id)
            if project_members_unknown:
                return cors_response(
                    request=request,
                    status_code=400,
                    body='Project member UUID reference Not Found: {0}'.format(', '.join(project_members_unknown)),
                    x_error='Project member UUID Unknown'
                )
        else:
            project_members_new = []

        # comanage project owners role
        if not comanage_projects_add_owners_put(uuid, project_owners_new):
            return cors_response(
                request=request,
                status_code=500,
                body='Unable to add owners: {0}'.format(str(uuid)),
                x_error='Unable to add owners in COmanage'
            )

        # comanage project memebers role
        if not comanage_projects_add_members_put(uuid, project_members_new):
            return cors_response(
                request=request,
                status_code=500,
                body='Unable to add members: {0}'.format(str(uuid)),
                x_error='Unable to add members in COmanage'
            )

        for person_uuid in project_owners:
            if person_uuid != DEFAULT_USER_UUID or config.getboolean('mock', 'data'):
                try:
                    # get people id
                    sql = """
                    SELECT id FROM fabric_people WHERE uuid = '{0}';
                    """.format(person_uuid)
                    dfq = dict_from_query(sql)
                    try:
                        people_id = dfq[0].get('id')
                    except IndexError or KeyError or TypeError as err:
                        print(err)
                        return cors_response(
                            request=request,
                            status_code=404,
                            body='Person UUID Not Found: {0}'.format(str(person_uuid)),
                            x_error='Person UUID Not Found'
                        )

                    # add to project_owners table
                    sql = """
                    INSERT INTO project_owners(projects_id, people_id)
                    VALUES ({0}, '{1}')
                    ON CONFLICT ON CONSTRAINT project_owners_duplicate
                    DO NOTHING
                    """.format(project_id, people_id)
                    sql_list.append(sql)

                    # add to project_members table
                    sql = """
                    INSERT INTO project_members(projects_id, people_id)
                    VALUES ({0}, '{1}')
                    ON CONFLICT ON CONSTRAINT project_members_duplicate
                    DO NOTHING
                    """.format(project_id, people_id)
                    sql_list.append(sql)

                except (Exception, psycopg2.DatabaseError) as error:
                    print(error)

    commands = tuple(i for i in sql_list)
    print("[INFO] attempt to add project owners data")
    run_sql_commands(commands)

    return projects_uuid_get(uuid)


def projects_add_tags_put(uuid, tags=None):  # noqa: E501
    """add tags to an existing project

    Add tags to an existing project # noqa: E501

    :param uuid:
    :type uuid: str
    :param tags: 
    :type tags: List[str]

    :rtype: ProjectLong
    """
    # validate project reference as provided by uuid
    project_id, project_name, created_by = validate_project_reference(uuid)
    if project_id == -1:
        return cors_response(
            request=request,
            status_code=400,
            body='Project UUID reference Not Found: {0}'.format(str(uuid)),
            x_error='Project UUID Unknown'
        )

    sql_list = []

    # check authorization
    if not authorize_projects_add_tags_put(request.headers):
        return cors_response(
            request=request,
            status_code=401,
            body='Authorization information is missing or invalid: /projects/add_tags',
            x_error='Authorization information is missing or invalid'
        )

    # check for new comanage users
    if not comanage_check_for_new_users():
        return cors_response(
            request=request,
            status_code=500,
            body='COmanage Error - Unable to retrieve co_people data',
            x_error='Unable to retrieve co_people data'
        )

    # resolve any missing people uuids
    resolve_empty_people_uuid()

    if tags:
        for tag in tags:
            if len(tag) > 0:
                sql = """
                INSERT INTO tags(projects_id, tag)
                VALUES ({0}, '{1}')
                ON CONFLICT ON CONSTRAINT tags_duplicate
                DO NOTHING
                """.format(project_id, tag.replace("'", "''"))
                sql_list.append(sql)
            else:
                return cors_response(
                    request=request,
                    status_code=400,
                    body='Bad Request, Tag not specified or is otherwise blank',
                    x_error='Bad Request, Tag not specified or is otherwise blank'
                )

    commands = tuple(i for i in sql_list)
    print("[INFO] attempt to update tags data")
    run_sql_commands(commands)

    return projects_uuid_get(uuid)


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
    # check authorization
    if tags:
        if not authorize_projects_add_tags_put(request.headers):
            return cors_response(
                request=request,
                status_code=401,
                body='Authorization information is missing or invalid: /projects/create with tags',
                x_error='Authorization information is missing or invalid'
            )

    if not authorize_projects_create_post(request.headers):
        return cors_response(
            request=request,
            status_code=401,
            body='Authorization information is missing or invalid: /projects/create',
            x_error='Authorization information is missing or invalid'
        )

    # check for new comanage users
    if not comanage_check_for_new_users():
        return cors_response(
            request=request,
            status_code=500,
            body='COmanage Error - Unable to retrieve co_people data',
            x_error='Unable to retrieve co_people data'
        )

    # resolve any missing people uuids
    resolve_empty_people_uuid()

    # get identity for created_by
    api_person = get_api_person(request.headers.get('X-Vouch-Idp-Idtoken'))
    created_by = api_person.uuid

    # validate new owners reference as provided by project_members
    if project_owners:
        project_owners.append(api_person.uuid)
    else:
        project_owners = [api_person.uuid]

    project_owners_new, project_owners_unknown = validate_person_reference(project_owners)
    if project_owners_unknown:
        return cors_response(
            request=request,
            status_code=400,
            body='Project owner UUID reference Not Found: {0}'.format(', '.join(project_owners_unknown)),
            x_error='Project owner UUID Unknown'
        )

    # validate new members reference as provided by project_members
    if project_members:
        project_members += project_owners_new.copy()
    else:
        project_members = project_owners_new.copy()

    project_members_new, project_members_unknown = validate_person_reference(project_members)
    if project_members_unknown:
        return cors_response(
            request=request,
            status_code=400,
            body='Project member UUID reference Not Found: {0}'.format(', '.join(project_members_unknown)),
            x_error='Project member UUID Unknown'
        )

    # get created_time
    t_now = datetime.utcnow()
    created_time = t_now.strftime("%Y-%m-%d %H:%M:%S")
    # create new project entry
    project_uuid = uuid4()
    sql = """
    INSERT INTO fabric_projects(uuid, name, description, facility, created_by, created_time)
    VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}');
    """.format(str(project_uuid), name.replace("'", "''"), description.replace("'", "''"), facility.replace("'", "''"),
               created_by, created_time)
    run_sql_commands(sql)

    # validate project reference as provided by uuid
    project_id, project_name, created_by = validate_project_reference(str(project_uuid))
    if project_id == -1:
        return cors_response(
            request=request,
            status_code=400,
            body='Project UUID reference Not Found: {0}'.format(str(project_uuid)),
            x_error='Project UUID Unknown'
        )

    # create comanage groups for project (uuid-po and uuid-pm)
    if not comanage_projects_create_post(project_uuid, name):
        return cors_response(
            request=request,
            status_code=500,
            body='Unable to create project: {0}'.format(str(project_uuid)),
            x_error='Unable to create project in COmanage'
        )

    # add projects creator to comanage uuid-pc group
    if not comanage_projects_add_creator_put(project_uuid, [created_by]):
        return cors_response(
            request=request,
            status_code=500,
            body='Unable to add creator: {0}'.format(str(project_uuid)),
            x_error='Unable to add creator in COmanage'
        )

    # add projects owners to comanage uuid-po group
    if not comanage_projects_add_owners_put(project_uuid, project_owners_new):
        return cors_response(
            request=request,
            status_code=500,
            body='Unable to add owners: {0}'.format(str(project_uuid)),
            x_error='Unable to add owners in COmanage'
        )

    # add project owners to database
    sql_list = []
    for person_uuid in project_owners_new:
        if person_uuid != DEFAULT_USER_UUID or config.getboolean('mock', 'data'):
            try:
                # get people id
                sql = """
                SELECT id FROM fabric_people WHERE uuid = '{0}';
                """.format(person_uuid)
                dfq = dict_from_query(sql)
                try:
                    people_id = dfq[0].get('id')
                except IndexError or KeyError or TypeError as err:
                    print(err)
                    projects_delete_delete(str(project_uuid))
                    return cors_response(
                        request=request,
                        status_code=400,
                        body='Person UUID Not Found: {0}'.format(str(person_uuid)),
                        x_error='Person UUID Not Found'
                    )

                # add to project_owners table
                sql = """
                INSERT INTO project_owners(projects_id, people_id)
                VALUES ({0}, '{1}')
                ON CONFLICT ON CONSTRAINT project_owners_duplicate
                DO NOTHING
                """.format(project_id, people_id)
                sql_list.append(sql)

            except (Exception, psycopg2.DatabaseError) as error:
                print(error)

    # add projects members to comanage uuid-pm group
    if not comanage_projects_add_members_put(project_uuid, project_members_new):
        return cors_response(
            request=request,
            status_code=500,
            body='Unable to add members: {0}'.format(str(project_uuid)),
            x_error='Unable to add members in COmanage'
        )

    # add project members to database
    for person_uuid in project_members_new:
        if person_uuid != DEFAULT_USER_UUID or config.getboolean('mock', 'data'):
            try:
                # get people id
                sql = """
                SELECT id FROM fabric_people WHERE uuid = '{0}';
                """.format(person_uuid)
                dfq = dict_from_query(sql)
                try:
                    people_id = dfq[0].get('id')
                except IndexError or KeyError or TypeError as err:
                    print(err)
                    projects_delete_delete(str(project_uuid))
                    return cors_response(
                        request=request,
                        status_code=404,
                        body='Person UUID Not Found: {0}'.format(str(person_uuid)),
                        x_error='Person UUID Not Found'
                    )

                # add to project_members table
                sql = """
                INSERT INTO project_members(projects_id, people_id)
                VALUES ({0}, '{1}')
                ON CONFLICT ON CONSTRAINT project_members_duplicate
                DO NOTHING
                """.format(project_id, people_id)
                sql_list.append(sql)

            except (Exception, psycopg2.DatabaseError) as error:
                print(error)

    # tags
    if tags:
        print(tags)
        for tag in tags:
            if len(tag) > 0:
                sql = """
                INSERT INTO tags(projects_id, tag)
                VALUES ({0}, '{1}')
                ON CONFLICT ON CONSTRAINT tags_duplicate
                DO NOTHING
                """.format(project_id, tag.replace("'", "''"))
                sql_list.append(sql)
            else:
                projects_delete_delete(str(project_uuid))
                return cors_response(
                    request=request,
                    status_code=400,
                    body='Bad Request, Tag not specified or is otherwise blank',
                    x_error='Bad Request, Tag not specified or is otherwise blank'
                )

    commands = tuple(i for i in sql_list)
    print("[INFO] attempt to update project data")
    run_sql_commands(commands)

    return projects_uuid_get(str(project_uuid))


def projects_delete_delete(uuid):  # noqa: E501
    """delete existing project

    Delete existing project # noqa: E501

    :param uuid: Project identifier as UUID
    :type uuid: str

    :rtype: None
    """
    # validate project reference as provided by uuid
    project_id, project_name, created_by = validate_project_reference(uuid)
    if project_id == -1:
        return cors_response(
            request=request,
            status_code=400,
            body='Project UUID reference Not Found: {0}'.format(str(uuid)),
            x_error='Project UUID Unknown'
        )

    # check authorization
    if not authorize_projects_delete_delete(request.headers, created_by):
        return cors_response(
            request=request,
            status_code=401,
            body='Authorization information is missing or invalid: /projects/delete',
            x_error='Authorization information is missing or invalid'
        )

    print("[WARNING] Deleting project: {0} ({1})".format(str(uuid), project_name))

    # remove projects_members from COU uuid-pm
    print("[WARNING] remove project members: {0}".format(str(uuid)))
    sql = """
    SELECT fabric_people.uuid
    FROM fabric_people INNER JOIN fabric_roles
    ON fabric_people.id = fabric_roles.people_id
    WHERE fabric_roles.role_name = '{0}';
    """.format(str(uuid) + '-pm')
    dfq = dict_from_query(sql)
    project_members = []
    if dfq:
        for member in dfq:
            project_members.append(member.get('uuid'))
        if not comanage_projects_remove_members_put(uuid, project_members):
            return cors_response(
                request=request,
                status_code=501,
                body='Unable to remove members: {0}'.format(str(uuid)),
                x_error='Unable to remove members in COmanage'
            )
        else:
            # remove project members
            command = """
            DELETE FROM project_members
            WHERE project_members.projects_id = {0};
            """.format(project_id)
            run_sql_commands(command)

    # remove project_owners from COU uuid-po
    print("[WARNING] remove project owners: {0}".format(str(uuid)))
    sql = """
    SELECT fabric_people.uuid
    FROM fabric_people INNER JOIN fabric_roles
    ON fabric_people.id = fabric_roles.people_id
    WHERE fabric_roles.role_name = '{0}';
    """.format(str(uuid) + '-po')
    dfq = dict_from_query(sql)
    project_owners = []
    if dfq:
        for member in dfq:
            project_owners.append(member.get('uuid'))
        if not comanage_projects_remove_owners_put(uuid, project_owners):
            return cors_response(
                request=request,
                status_code=501,
                body='Unable to remove owners: {0}'.format(str(uuid)),
                x_error='Unable to remove owners in COmanage'
            )
        else:
            # remove project owners
            command = """
            DELETE FROM project_owners
            WHERE project_owners.projects_id = {0};
            """.format(project_id)
            run_sql_commands(command)

    # remove project creator from COU uuid-pc
    print("[WARNING] remove project creator: {0}".format(str(uuid)))
    sql = """
    SELECT fabric_people.uuid
    FROM fabric_people INNER JOIN fabric_roles
    ON fabric_people.id = fabric_roles.people_id
    WHERE fabric_roles.role_name = '{0}';
    """.format(str(uuid) + '-pc')
    dfq = dict_from_query(sql)
    project_creators = []
    if dfq:
        for member in dfq:
            project_creators.append(member.get('uuid'))
        print(project_creators)
        if not comanage_projects_remove_creators(uuid, project_creators):
            return cors_response(
                request=request,
                status_code=501,
                body='Unable to remove creators: {0}'.format(str(uuid)),
                x_error='Unable to remove project creator in COmanage'
            )

    # remove project tags
    print("[WARNING] remove project tags: {0}".format(str(uuid)))
    command = """
    DELETE FROM tags
    WHERE tags.projects_id = {0};
    """.format(project_id)
    run_sql_commands(command)

    # remove project COU uuid-pc, uuid-po, uuid-pm
    print("[WARNING] remove project COUs: {0}".format(str(uuid)))
    if not comanage_projects_delete_delete(uuid):
        return cors_response(
            request=request,
            status_code=501,
            body='Unable to delete project COUs: {0}'.format(str(uuid)),
            x_error='Unable to delete project in COmanage'
        )
    else:
        # remove project
        command = """
        DELETE FROM fabric_projects
        WHERE fabric_projects.uuid = '{0}';
        """.format(uuid)
        run_sql_commands(command)

    print("[INFO] project successfully removed: {0}".format(str(uuid)))

    return {}


def projects_get(project_name=None):  # noqa: E501
    """list of projects

    List of projects # noqa: E501

    :param project_name: Search Project by Name (ILIKE)
    :type project_name: str

    :rtype: ProjectShort
    """
    # check authorization
    if not authorize_projects_get(request.headers):
        return cors_response(
            request=request,
            status_code=401,
            body='Authorization information is missing or invalid: /projects',
            x_error='Authorization information is missing or invalid'
        )
    # response as array of ProjectShort()
    response = []

    sql = """
    SELECT name, description, facility, uuid, created_by, created_time FROM fabric_projects
    """

    if project_name:
        sql = sql + """
        WHERE name ILIKE '%{}%'
        """.format(str(project_name))

    sql = sql + """
    ORDER BY name;
    """
    dfq = dict_from_query(sql)

    # construct response object
    if dfq:
        for project in dfq:
            # project object
            ps = ProjectShort()

            # project created by
            pc = people_uuid_get(project.get('created_by'))
            try:
                created_by = {'uuid': pc.uuid, 'name': pc.name, 'email': pc.email}
            except AttributeError:
                created_by = {'uuid': DEFAULT_USER_UUID, 'name': DEFAULT_USER_NAME, 'email': DEFAULT_USER_EMAIL}

            ps.name = project.get('name')
            ps.description = project.get('description')
            ps.facility = project.get('facility')
            ps.uuid = project.get('uuid')
            ps.created_by = created_by
            ps.created_time = project.get('created_time')
            response.append(ps)

    return filter_projects_get(request.headers, response)


def projects_remove_members_put(uuid, project_members=None):  # noqa: E501
    """remove members to an existing project

    Remove members to an existing project # noqa: E501

    :param uuid:
    :type uuid: str
    :param project_members: Array of project members as UUID
    :type project_members: List[str]

    :rtype: ProjectLong
    """
    # validate project reference as provided by uuid
    project_id, project_name, created_by = validate_project_reference(uuid)
    if project_id == -1:
        return cors_response(
            request=request,
            status_code=400,
            body='Project UUID reference Not Found: {0}'.format(str(uuid)),
            x_error='Project UUID Unknown'
        )

    sql_list = []

    # check authorization
    if not authorize_projects_remove_members_put(request.headers, uuid, created_by):
        return cors_response(
            request=request,
            status_code=401,
            body='Authorization information is missing or invalid: /projects/remove_members',
            x_error='Authorization information is missing or invalid'
        )

    if project_members:
        project_members = filter_out_nonexisting_project_members(list(set(project_members)), project_id)
        if not comanage_projects_remove_members_put(uuid, project_members):
            return cors_response(
                request=request,
                status_code=501,
                body='Unable to remove members: {0}'.format(str(uuid)),
                x_error='Unable to remove members in COmanage'
            )

        for person_uuid in project_members:
            if person_uuid != DEFAULT_USER_UUID:
                try:
                    # get people id
                    sql = """
                    SELECT id FROM fabric_people WHERE uuid = '{0}';
                    """.format(person_uuid)
                    dfq = dict_from_query(sql)
                    try:
                        people_id = dfq[0].get('id')
                    except IndexError or KeyError or TypeError as err:
                        print(err)
                        return cors_response(
                            request=request,
                            status_code=501,
                            body='Person UUID Not Found: {0}'.format(str(person_uuid)),
                            x_error='Person UUID Not Found'
                        )

                    # remove people_id from project_members table
                    sql = """
                    DELETE FROM project_members
                    WHERE project_members.projects_id = {0} AND project_members.people_id = {1};
                    """.format(project_id, people_id)
                    sql_list.append(sql)

                    # check if person is also in project_owners
                    sql_po_check = """
                    SELECT EXISTS (
                    SELECT 1 FROM project_owners 
                    WHERE project_owners.projects_id = {0} and project_owners.people_id = {1}
                    );
                    """.format(project_id, people_id)
                    dfq = dict_from_query(sql_po_check)
                    if dfq[0].get('exists'):
                        project_owners = [person_uuid]
                        if not comanage_projects_remove_owners_put(uuid, project_owners):
                            return cors_response(
                                request=request,
                                status_code=501,
                                body='Unable to remove owners: {0}'.format(str(uuid)),
                                x_error='Unable to remove owners in COmanage'
                            )

                        # remove people_id from project_owners table
                        sql = """
                        DELETE FROM project_owners
                        WHERE project_owners.projects_id = {0} AND project_owners.people_id = {1};
                        """.format(project_id, people_id)
                        sql_list.append(sql)

                except (Exception, psycopg2.DatabaseError) as error:
                    print(error)

    commands = tuple(i for i in sql_list)
    print("[INFO] attempt to remove project members data")
    run_sql_commands(commands)

    return projects_uuid_get(uuid)


def projects_remove_owners_put(uuid, project_owners=None):  # noqa: E501
    """remove owners to an existing project

    Remove owners to an existing project # noqa: E501

    :param uuid:
    :type uuid: str
    :param project_owners: Array of project owners as UUID
    :type project_owners: List[str]

    :rtype: ProjectLong
    """
    # validate project reference as provided by uuid
    project_id, project_name, created_by = validate_project_reference(uuid)
    if project_id == -1:
        return cors_response(
            request=request,
            status_code=400,
            body='Project UUID reference Not Found: {0}'.format(str(uuid)),
            x_error='Project UUID Unknown'
        )

    sql_list = []

    # check authorization
    if not authorize_projects_remove_owners_put(request.headers, created_by):
        return cors_response(
            request=request,
            status_code=401,
            body='Authorization information is missing or invalid: /projects/remove_owners',
            x_error='Authorization information is missing or invalid'
        )

    if project_owners:
        project_owners = filter_out_nonexisting_project_owners(list(set(project_owners)), project_id)
        if not comanage_projects_remove_owners_put(uuid, project_owners):
            return cors_response(
                request=request,
                status_code=501,
                body='Unable to remove owners: {0}'.format(str(uuid)),
                x_error='Unable to remove owners in COmanage'
            )
        for person_uuid in project_owners:
            if person_uuid != DEFAULT_USER_UUID:
                try:
                    # get people id
                    sql = """
                    SELECT id FROM fabric_people WHERE uuid = '{0}';
                    """.format(person_uuid)
                    dfq = dict_from_query(sql)
                    try:
                        people_id = dfq[0].get('id')
                    except IndexError or KeyError or TypeError as err:
                        print(err)
                        return cors_response(
                            request=request,
                            status_code=404,
                            body='Person UUID Not Found: {0}'.format(str(person_uuid)),
                            x_error='Person UUID Not Found'
                        )

                    # remove people_id from project_owners table
                    sql = """
                    DELETE FROM project_owners
                    WHERE project_owners.projects_id = {0} AND project_owners.people_id = {1};
                    """.format(project_id, people_id)
                    sql_list.append(sql)

                except (Exception, psycopg2.DatabaseError) as error:
                    print(error)

    commands = tuple(i for i in sql_list)
    print("[INFO] attempt to remove project owners data")
    run_sql_commands(commands)

    return projects_uuid_get(uuid)


def projects_remove_tags_put(uuid, tags=None):  # noqa: E501
    """remove tags to an existing project

    Remove tags to an existing project # noqa: E501

    :param uuid:
    :type uuid: str
    :param tags: 
    :type tags: List[str]

    :rtype: ProjectLong
    """
    # validate project reference as provided by uuid
    project_id, project_name, created_by = validate_project_reference(uuid)
    if project_id == -1:
        return cors_response(
            request=request,
            status_code=400,
            body='Project UUID reference Not Found: {0}'.format(str(uuid)),
            x_error='Project UUID Unknown'
        )

    sql_list = []

    # check authorization
    if not authorize_projects_remove_tags_put(request.headers, uuid, created_by):
        return cors_response(
            request=request,
            status_code=401,
            body='Authorization information is missing or invalid: /projects/remove_tags',
            x_error='Authorization information is missing or invalid'
        )

    if tags:
        print(tags)
        for tag in tags:
            if len(tag) > 0:
                sql = """
                DELETE FROM tags
                WHERE tags.projects_id = {0} AND tags.tag = '{1}'
                """.format(project_id, tag)
                sql_list.append(sql)
            else:
                return cors_response(
                    request=request,
                    status_code=400,
                    body='Bad Request, Tag not specified or is otherwise blank',
                    x_error='Bad Request, Tag not specified or is otherwise blank'
                )

    commands = tuple(i for i in sql_list)
    print("[INFO] attempt to remove tags data")
    run_sql_commands(commands)

    return projects_uuid_get(uuid)


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
    # validate project reference as provided by uuid
    project_id, project_name, created_by = validate_project_reference(uuid)
    if project_id == -1:
        return cors_response(
            request=request,
            status_code=400,
            body='Project UUID reference Not Found: {0}'.format(str(uuid)),
            x_error='Project UUID Unknown'
        )

    sql_list = []

    # check authorization
    if not authorize_projects_update_put(request.headers, created_by):
        return cors_response(
            request=request,
            status_code=401,
            body='Authorization information is missing or invalid: /projects/update',
            x_error='Authorization information is missing or invalid'
        )

    if name:
        sql = """
        UPDATE fabric_projects
        SET name = '{0}'
        WHERE fabric_projects.id = {1};
        """.format(name.replace("'", "''"), project_id)
        sql_list.append(sql)
    if description:
        sql = """
        UPDATE fabric_projects
        SET description = '{0}'
        WHERE fabric_projects.id = {1};
        """.format(description.replace("'", "''"), project_id)
        sql_list.append(sql)
    if facility:
        sql = """
        UPDATE fabric_projects
        SET facility = '{0}'
        WHERE fabric_projects.id = {1};
        """.format(facility.replace("'", "''"), project_id)
        sql_list.append(sql)

    commands = tuple(i for i in sql_list)
    print("[INFO] attempt to update project data")
    run_sql_commands(commands)

    return projects_uuid_get(uuid)


def projects_uuid_get(uuid):  # noqa: E501
    """project details

    Project details # noqa: E501

    :param uuid: Project identifier as UUID
    :type uuid: str

    :rtype: ProjectLong
    """
    # response as ProjectLong()
    response = ProjectLong()

    # validate project reference as provided by uuid
    project_id, project_name, created_by = validate_project_reference(uuid)
    if project_id == -1:
        return cors_response(
            request=request,
            status_code=400,
            body='Project UUID reference Not Found: {0}'.format(str(uuid)),
            x_error='Project UUID Unknown'
        )

    # check authorization
    if not authorize_projects_uuid_get(request.headers, uuid, created_by):
        return cors_response(
            request=request,
            status_code=401,
            body='Authorization information is missing or invalid: /projects/{uuid}',
            x_error='Authorization information is missing or invalid'
        )

    # get project attributes
    project_sql = """
    SELECT * FROM fabric_projects
    WHERE uuid = '{0}';
    """.format(uuid)
    project = dict_from_query(project_sql)[0]

    # project created by
    cb_sql = """
    SELECT uuid, name, email FROM fabric_people
    WHERE uuid = '{0}';
    """.format(project.get('created_by'))
    pc = dict_from_query(cb_sql)
    created_by = {'uuid': pc[0].get('uuid'), 'name': pc[0].get('name'), 'email': pc[0].get('email')}

    # project-owners
    project_owners = []
    po_sql = """
    SELECT uuid, name, email FROM fabric_people
    INNER JOIN project_owners ON fabric_people.id = project_owners.people_id 
    AND project_owners.projects_id = {0};
    """.format(project_id)
    dfq = dict_from_query(po_sql)
    for po in dfq:
        project_owners.append({'uuid': po.get('uuid'), 'name': po.get('name'), 'email': po.get('email')})

    # project-members
    project_members = []
    pm_sql = """
    SELECT uuid, name, email FROM fabric_people
    INNER JOIN project_members ON fabric_people.id = project_members.people_id 
    AND project_members.projects_id = {0};
    """.format(project_id)
    dfq = dict_from_query(pm_sql)
    for pm in dfq:
        project_members.append({'uuid': pm.get('uuid'), 'name': pm.get('name'), 'email': pm.get('email')})

    # tags
    tags = []
    tags_sql = """
    SELECT tag FROM tags
    WHERE projects_id = {0}
    ORDER BY tag;
    """.format(project_id)
    dfq = dict_from_query(tags_sql)
    for tag in dfq:
        tags.append(tag.get('tag'))

    # construct response object
    response.name = project.get('name')
    response.description = project.get('description')
    response.facility = project.get('facility')
    response.uuid = project.get('uuid')
    response.created_by = created_by
    response.created_time = project.get('created_time')
    response.project_owners = project_owners
    response.project_members = project_members
    response.tags = tags

    return response
