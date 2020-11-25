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
from .utils import dict_from_query, run_sql_commands, resolve_empty_people_uuid
from ..authorization.people import get_api_person
from ..authorization.projects import filter_projects_get, authorize_projects_add_members_put, \
    authorize_projects_add_owners_put, authorize_projects_add_tags_put, authorize_projects_create_post, \
    authorize_projects_delete_delete, authorize_projects_get, authorize_projects_remove_members_put, \
    authorize_projects_remove_owners_put, authorize_projects_remove_tags_put, authorize_projects_update_put, \
    authorize_projects_uuid_get, DEFAULT_USER_UUID
from ..comanage_api.comanage_api import comanage_projects_add_members_put, comanage_projects_add_owners_put, \
    comanage_projects_remove_members_put, comanage_projects_remove_owners_put, comanage_projects_create_post

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
    sql_list = []
    # get project id
    sql = """
    SELECT id, created_by FROM fabric_projects WHERE uuid = '{0}';
    """.format(uuid)
    dfq = dict_from_query(sql)
    try:
        project_id = dfq[0].get('id')
        created_by = dfq[0].get('created_by')
    except IndexError:
        return 'Project UUID Not Found: {0}'.format(str(uuid)), 404, {'X-Error': 'Project UUID Not Found'}

    # check authorization
    if not authorize_projects_add_members_put(request.headers, uuid, created_by):
        return 'Authorization information is missing or invalid: /projects/add_members', 401, \
               {'X-Error': 'Authorization information is missing or invalid'}

    # resolve any missing people uuids
    resolve_empty_people_uuid()

    if project_members:
        if not comanage_projects_add_members_put(uuid, project_members):
            return 'Unable to add members: {0}'.format(str(uuid)), 501, \
                   {'X-Error': 'Unable to add members in COmanage'}

        # get role_name and cou_id for -pm
        role_name_pm = str(uuid) + '-pm'
        sql = """
        SELECT id from comanage_cous WHERE name = '{0}';
        """.format(role_name_pm)
        cou_id_pm = dict_from_query(sql)[0].get('id')

        for person_uuid in project_members:
            if person_uuid != DEFAULT_USER_UUID or config.getboolean('mock', 'data'):
                try:
                    # get people id
                    sql = """
                    SELECT id from fabric_people WHERE uuid = '{0}';
                    """.format(person_uuid)
                    dfq = dict_from_query(sql)
                    try:
                        people_id = dfq[0].get('id')
                    except IndexError:
                        return 'Person UUID Not Found: {0}'.format(str(person_uuid)), 404, \
                               {'X-Error': 'Person UUID Not Found'}

                    # add to project_members table
                    sql = """
                    INSERT INTO project_members(projects_id, people_id)
                    VALUES ({0}, '{1}')
                    ON CONFLICT ON CONSTRAINT project_members_duplicate
                    DO NOTHING
                    """.format(project_id, people_id)
                    sql_list.append(sql)

                    # add cou to fabric_roles table
                    sql = """
                    INSERT INTO fabric_roles(people_id, cou_id, role_name)
                    VALUES ({0}, {1}, '{2}')
                    ON CONFLICT ON CONSTRAINT fabric_role_duplicate
                    DO NOTHING
                    """.format(people_id, cou_id_pm, role_name_pm)
                    sql_list.append(sql)

                except (Exception, psycopg2.DatabaseError) as error:
                    print(error)
                    pass

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
    sql_list = []
    # get project id
    sql = """
    SELECT id, created_by FROM fabric_projects WHERE uuid = '{0}';
    """.format(uuid)
    dfq = dict_from_query(sql)
    try:
        project_id = dfq[0].get('id')
        created_by = dfq[0].get('created_by')
    except IndexError:
        return 'Project UUID Not Found: {0}'.format(str(uuid)), 404, {'X-Error': 'Project UUID Not Found'}

    # check authorization
    if not authorize_projects_add_owners_put(request.headers, created_by):
        return 'Authorization information is missing or invalid: /projects/add_owners', 401, \
               {'X-Error': 'Authorization information is missing or invalid'}

    # resolve any missing people uuids
    resolve_empty_people_uuid()

    if project_owners:
        if not comanage_projects_add_owners_put(uuid, project_owners):
            return 'Unable to add owners: {0}'.format(str(uuid)), 501, \
                   {'X-Error': 'Unable to add owners in COmanage'}

        # get role_name and cou_id for -po and -pm
        role_name_po = str(uuid) + '-po'
        sql = """
        SELECT id from comanage_cous WHERE name = '{0}';
        """.format(role_name_po)
        cou_id_po = dict_from_query(sql)[0].get('id')

        role_name_pm = str(uuid) + '-pm'
        sql = """
        SELECT id from comanage_cous WHERE name = '{0}';
        """.format(role_name_pm)
        cou_id_pm = dict_from_query(sql)[0].get('id')

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
                    except IndexError:
                        return 'Person UUID Not Found: {0}'.format(str(person_uuid)), 404, \
                               {'X-Error': 'Person UUID Not Found'}

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

                    # add -po cou to fabric_roles table
                    sql = """
                    INSERT INTO fabric_roles(people_id, cou_id, role_name)
                    VALUES ({0}, '{1}', '{2}')
                    ON CONFLICT ON CONSTRAINT fabric_role_duplicate
                    DO NOTHING
                    """.format(people_id, cou_id_po, role_name_po)
                    sql_list.append(sql)

                    # add -pm cou to fabric_roles table
                    sql = """
                    INSERT INTO fabric_roles(people_id, cou_id, role_name)
                    VALUES ({0}, '{1}', '{2}')
                    ON CONFLICT ON CONSTRAINT fabric_role_duplicate
                    DO NOTHING
                    """.format(people_id, cou_id_pm, role_name_pm)
                    sql_list.append(sql)

                except (Exception, psycopg2.DatabaseError) as error:
                    print(error)
                    pass

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
    sql_list = []
    # get project id
    sql = """
        SELECT id, created_by FROM fabric_projects WHERE uuid = '{0}';
        """.format(uuid)
    dfq = dict_from_query(sql)
    try:
        project_id = dfq[0].get('id')
        created_by = dfq[0].get('created_by')
    except IndexError:
        return 'Project UUID Not Found: {0}'.format(str(uuid)), 404, {'X-Error': 'Project UUID Not Found'}

    # check authorization
    if not authorize_projects_add_tags_put(request.headers):
        return 'Authorization information is missing or invalid: /projects/add_tags', 401, \
               {'X-Error': 'Authorization information is missing or invalid'}

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
                return 'Bad Request, Tag not specified or is otherwise blank', 400, \
                       {'X-Error': 'Bad Request, Tag not specified or is otherwise blank'}

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
            return 'Authorization information is missing or invalid: /projects/create with tags', 401, \
                   {'X-Error': 'Authorization information is missing or invalid'}

    if not authorize_projects_create_post(request.headers):
        return 'Authorization information is missing or invalid: /projects/create', 401, \
               {'X-Error': 'Authorization information is missing or invalid'}

    # resolve any missing people uuids
    resolve_empty_people_uuid()

    # get identity for created_by
    api_person = get_api_person(request.headers.get('X-Vouch-Idp-Idtoken'))
    created_by = api_person.uuid

    # get created_time
    t_now = datetime.now()
    t_zone = timezone('America/New_York')
    created_time = t_zone.localize(t_now)
    # create new project entry
    project_uuid = uuid4()
    sql = """
    INSERT INTO fabric_projects(uuid, name, description, facility, created_by, created_time)
    VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}');
    """.format(str(project_uuid), name.replace("'", "''"), description.replace("'", "''"), facility.replace("'", "''"),
               created_by, created_time)
    run_sql_commands(sql)

    sql_list = []
    # get project id
    sql = """
    SELECT id FROM fabric_projects WHERE uuid = '{0}';
    """.format(project_uuid)
    dfq = dict_from_query(sql)
    try:
        project_id = dfq[0].get('id')
    except IndexError:
        projects_delete_delete(str(project_uuid))
        return 'Project UUID Not Found: {0}'.format(str(uuid)), 404, {'X-Error': 'Project UUID Not Found'}

    if not comanage_projects_create_post(project_uuid):
        return 'Unable to create project: {0}'.format(str(uuid)), 501, \
               {'X-Error': 'Unable to create project in COmanage'}

    # project owners
    if project_owners:
        project_owners.append(api_person.uuid)
    else:
        project_owners = [api_person.uuid]
    if project_owners:
        if not comanage_projects_add_owners_put(project_uuid, project_owners):
            return 'Unable to add owners: {0}'.format(str(uuid)), 501, \
                   {'X-Error': 'Unable to add owners in COmanage'}

        # get role_name and cou_id for -po and -pm
        role_name_po = str(uuid) + '-po'
        sql = """
        SELECT id from comanage_cous WHERE name = '{0}';
        """.format(role_name_po)
        cou_id_po = dict_from_query(sql)[0].get('id')

        role_name_pm = str(uuid) + '-pm'
        sql = """
        SELECT id from comanage_cous WHERE name = '{0}';
        """.format(role_name_pm)
        cou_id_pm = dict_from_query(sql)[0].get('id')

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
                    except IndexError:
                        projects_delete_delete(str(project_uuid))
                        return 'Person UUID Not Found: {0}'.format(str(person_uuid)), 404, \
                               {'X-Error': 'Person UUID Not Found'}

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

                    # add cou to fabric_roles table
                    sql = """
                    INSERT INTO fabric_roles(people_id, cou_id, role_name)
                    VALUES ({0}, '{1}', '{2}')
                    ON CONFLICT ON CONSTRAINT fabric_role_duplicate
                    DO NOTHING
                    """.format(people_id, cou_id_po, role_name_po)
                    sql_list.append(sql)

                    # add cou to fabric_roles table
                    cou = str(project_uuid) + '-pm'
                    sql = """
                    INSERT INTO fabric_roles(people_id, cou_id, role_name)
                    VALUES ({0}, '{1}', '{2}')
                    ON CONFLICT ON CONSTRAINT fabric_role_duplicate
                    DO NOTHING
                    """.format(people_id, cou_id_pm, role_name_pm)
                    sql_list.append(sql)

                except (Exception, psycopg2.DatabaseError) as error:
                    print(error)
                    pass
    # project members
    if project_members:
        if not comanage_projects_add_members_put(project_uuid, project_members):
            return 'Unable to add members: {0}'.format(str(uuid)), 501, \
                   {'X-Error': 'Unable to add members in COmanage'}

        # get role_name and cou_id for -pm
        role_name_pm = str(uuid) + '-pm'
        sql = """
        SELECT id from comanage_cous WHERE name = '{0}';
        """.format(role_name_pm)
        cou_id_pm = dict_from_query(sql)[0].get('id')

        for person_uuid in project_members:
            if person_uuid != DEFAULT_USER_UUID or config.getboolean('mock', 'data'):
                try:
                    # get people id
                    sql = """
                    SELECT id FROM fabric_people WHERE uuid = '{0}';
                    """.format(person_uuid)
                    dfq = dict_from_query(sql)
                    try:
                        people_id = dfq[0].get('id')
                    except IndexError:
                        projects_delete_delete(str(project_uuid))
                        return 'Person UUID Not Found: {0}'.format(str(person_uuid)), 404, \
                               {'X-Error': 'Person UUID Not Found'}

                    # add to project_members table
                    sql = """
                    INSERT INTO project_members(projects_id, people_id)
                    VALUES ({0}, '{1}')
                    ON CONFLICT ON CONSTRAINT project_members_duplicate
                    DO NOTHING
                    """.format(project_id, people_id)
                    sql_list.append(sql)

                    # add cou to fabric_roles table
                    cou = str(project_uuid) + '-pm'
                    sql = """
                    INSERT INTO fabric_roles(people_id, cou_id, role_name)
                    VALUES ({0}, '{1}', '{2}')
                    ON CONFLICT ON CONSTRAINT fabric_role_duplicate
                    DO NOTHING
                    """.format(people_id, cou_id_pm, role_name_pm)
                    sql_list.append(sql)
                except (Exception, psycopg2.DatabaseError) as error:
                    print(error)
                    pass

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
                return 'Bad Request, Tag not specified or is otherwise blank', 400, \
                       {'X-Error': 'Bad Request, Tag not specified or is otherwise blank'}

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
    sql_list = []
    # get project id
    sql = """
    SELECT id, created_by FROM fabric_projects WHERE uuid = '{0}';
    """.format(uuid)
    dfq = dict_from_query(sql)
    try:
        project_id = dfq[0].get('id')
        created_by = dfq[0].get('created_by')
    except IndexError:
        return 'Project UUID Not Found: {0}'.format(str(uuid)), 404, {'X-Error': 'Project UUID Not Found'}

    # check authorization
    if not authorize_projects_delete_delete(request.headers, created_by):
        return 'Authorization information is missing or invalid: /projects/delete', 401, \
               {'X-Error': 'Authorization information is missing or invalid'}
    # TODO: get list of project_owners
    project_owners = []
    if not comanage_projects_remove_owners_put(uuid, project_owners):
        return 'Unable to remove owners: {0}'.format(str(uuid)), 501, \
               {'X-Error': 'Unable to remove owners in COmanage'}
    # TODO: get list of project_members
    project_members = []
    if not comanage_projects_remove_members_put(uuid, project_members):
        return 'Unable to remove members: {0}'.format(str(uuid)), 501, \
               {'X-Error': 'Unable to remove members in COmanage'}

    # project owners
    sql = """
    DELETE FROM project_owners
    WHERE project_owners.projects_id = {0};
    """.format(project_id)
    sql_list.append(sql)

    # project members
    sql = """
    DELETE FROM project_members
    WHERE project_members.projects_id = {0};
    """.format(project_id)
    sql_list.append(sql)

    # tags
    sql = """
    DELETE FROM tags
    WHERE tags.projects_id = {0};
    """.format(project_id)
    sql_list.append(sql)

    # roles
    sql = """
    DELETE FROM fabric_roles
    WHERE fabric_roles.role_name LIKE '%{0}%';
    """.format(uuid)
    sql_list.append(sql)

    # project
    sql = """
    DELETE FROM fabric_projects
    WHERE fabric_projects.uuid = '{0}';
    """.format(uuid)
    sql_list.append(sql)

    commands = tuple(i for i in sql_list)
    print("[INFO] attempt to remove project owners data")
    run_sql_commands(commands)

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
        return 'Authorization information is missing or invalid: /projects', 401, \
               {'X-Error': 'Authorization information is missing or invalid'}

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
    sql_list = []
    # get project id
    sql = """
    SELECT id, created_by FROM fabric_projects WHERE uuid = '{0}';
    """.format(uuid)
    dfq = dict_from_query(sql)
    try:
        project_id = dfq[0].get('id')
        created_by = dfq[0].get('created_by')
    except IndexError:
        return 'Project UUID Not Found: {0}'.format(str(uuid)), 404, {'X-Error': 'Project UUID Not Found'}

    # check authorization
    if not authorize_projects_remove_members_put(request.headers, uuid, created_by):
        return 'Authorization information is missing or invalid: /projects/remove_members', 401, \
               {'X-Error': 'Authorization information is missing or invalid'}

    if project_members:
        if not comanage_projects_remove_members_put(uuid, project_members):
            return 'Unable to remove members: {0}'.format(str(uuid)), 501, \
                   {'X-Error': 'Unable to remove members in COmanage'}
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
                    except IndexError:
                        return 'Person UUID Not Found: {0}'.format(str(person_uuid)), 404, \
                               {'X-Error': 'Person UUID Not Found'}

                    # remove people_id from project_members table
                    sql = """
                    DELETE FROM project_members
                    WHERE project_members.projects_id = {0} AND project_members.people_id = {1};
                    """.format(project_id, people_id)
                    sql_list.append(sql)

                    # remove -pm cou from fabric_roles table
                    cou = str(uuid) + '-pm'
                    sql = """
                    DELETE FROM fabric_roles
                    WHERE fabric_roles.people_id = {0} AND role_name = '{1}';
                    """.format(people_id, cou)
                    sql_list.append(sql)

                    # check if person is also in project_owners
                    sql_po_check = """
                    SELECT EXISTS (
                        SELECT 1 FROM project_owners 
                        WHERE project_owners.projects_id = {0} and project_owners.people_id = {1}
                    );
                    """.format(project_id, people_id)
                    dfq = dict_from_query(sql_po_check)
                    print(dfq[0])
                    if dfq[0].get('exists'):
                        # remove people_id from project_owners table
                        sql = """
                        DELETE FROM project_owners
                        WHERE project_owners.projects_id = {0} AND project_owners.people_id = {1};
                        """.format(project_id, people_id)
                        sql_list.append(sql)

                        # remove -po cou from fabric_roles table
                        cou = str(uuid) + '-po'
                        sql = """
                        DELETE FROM fabric_roles
                        WHERE fabric_roles.people_id = {0} AND role_name = '{1}';
                        """.format(people_id, cou)
                        sql_list.append(sql)

                except (Exception, psycopg2.DatabaseError) as error:
                    print(error)
                    pass

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
    sql_list = []
    # get project id
    sql = """
    SELECT id, created_by FROM fabric_projects WHERE uuid = '{0}';
    """.format(uuid)
    dfq = dict_from_query(sql)
    try:
        project_id = dfq[0].get('id')
        created_by = dfq[0].get('created_by')
    except IndexError:
        return 'Project UUID Not Found: {0}'.format(str(uuid)), 404, {'X-Error': 'Project UUID Not Found'}

    # check authorization
    if not authorize_projects_remove_owners_put(request.headers, created_by):
        return 'Authorization information is missing or invalid: /projects/remove_owners', 401, \
               {'X-Error': 'Authorization information is missing or invalid'}

    if project_owners:
        if not comanage_projects_remove_owners_put(uuid, project_owners):
            return 'Unable to remove owners: {0}'.format(str(uuid)), 501, \
                   {'X-Error': 'Unable to remove owners in COmanage'}
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
                    except IndexError:
                        return 'Person UUID Not Found: {0}'.format(str(person_uuid)), 404, \
                               {'X-Error': 'Person UUID Not Found'}

                    # remove people_id from project_owners table
                    sql = """
                    DELETE FROM project_owners
                    WHERE project_owners.projects_id = {0} AND project_owners.people_id = {1};
                        """.format(project_id, people_id)
                    sql_list.append(sql)

                    # remove cou from fabric_roles table
                    cou = str(uuid) + '-pm'
                    sql = """
                    DELETE FROM fabric_roles
                    WHERE fabric_roles.people_id = {0} AND role_name = '{1}';
                    """.format(people_id, cou)
                    sql_list.append(sql)

                except (Exception, psycopg2.DatabaseError) as error:
                    print(error)
                    pass

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
    sql_list = []
    # get project id
    sql = """
    SELECT id, created_by FROM fabric_projects WHERE uuid = '{0}';
    """.format(uuid)
    dfq = dict_from_query(sql)
    try:
        project_id = dfq[0].get('id')
        created_by = dfq[0].get('created_by')
    except IndexError:
        return 'Project UUID Not Found: {0}'.format(str(uuid)), 404, {'X-Error': 'Project UUID Not Found'}

    # check authorization
    if not authorize_projects_remove_tags_put(request.headers, uuid, created_by):
        return 'Authorization information is missing or invalid: /projects/remove_tags', 401, \
               {'X-Error': 'Authorization information is missing or invalid'}

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
                return 'Bad Request, Tag not specified or is otherwise blank', 400, \
                       {'X-Error': 'Bad Request, Tag not specified or is otherwise blank'}

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
    sql_list = []
    # get project id
    sql = """
    SELECT id, created_by FROM fabric_projects WHERE uuid = '{0}';
    """.format(uuid)
    dfq = dict_from_query(sql)
    try:
        project_id = dfq[0].get('id')
        created_by = dfq[0].get('created_by')
    except IndexError:
        return 'Project UUID Not Found: {0}'.format(str(uuid)), 404, {'X-Error': 'Project UUID Not Found'}

    # check authorization
    if not authorize_projects_update_put(request.headers, created_by):
        return 'Authorization information is missing or invalid: /projects/update', 401, \
               {'X-Error': 'Authorization information is missing or invalid'}

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

    # get project id
    sql = """
    SELECT id, created_by FROM fabric_projects WHERE uuid = '{0}';
    """.format(uuid)
    dfq = dict_from_query(sql)
    try:
        project_id = dfq[0].get('id')
        created_by = dfq[0].get('created_by')
    except IndexError:
        return 'Project UUID Not Found: {0}'.format(str(uuid)), 404, {'X-Error': 'Project UUID Not Found'}

    # check authorization
    if not authorize_projects_uuid_get(request.headers, uuid, created_by):
        return 'Authorization information is missing or invalid: /projects/{uuid}', 401, \
               {'X-Error': 'Authorization information is missing or invalid'}

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
