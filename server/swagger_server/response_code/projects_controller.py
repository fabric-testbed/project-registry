from uuid import uuid4

import psycopg2
from swagger_server.models.project_long import ProjectLong  # noqa: E501
from swagger_server.models.project_short import ProjectShort  # noqa: E501

from .utils import dict_from_query, run_sql_commands

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
    SELECT id from fabric_projects WHERE uuid = '{0}';
    """.format(uuid)
    dfq = dict_from_query(sql)
    project_id = dfq[0]['id']

    if project_members:
        for person_uuid in project_members:
            try:
                # get people id
                sql = """
                SELECT id from fabric_people WHERE uuid = '{0}';
                """.format(person_uuid)
                dfq = dict_from_query(sql)
                people_id = dfq[0]['id']

                # add to project_members table
                sql = """
                INSERT INTO project_members(projects_id, people_id)
                VALUES ({0}, '{1}')
                ON CONFLICT ON CONSTRAINT project_members_duplicate
                DO NOTHING
                """.format(project_id, people_id)
                sql_list.append(sql)

                # add cou to roles table
                cou = 'CO:COU:' + str(uuid) + '-pm:members:active'
                sql = """
                INSERT INTO roles(people_id, role)
                VALUES ({0}, '{1}')
                ON CONFLICT ON CONSTRAINT roles_duplicate
                DO NOTHING
                """.format(people_id, cou)
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
        SELECT id from fabric_projects WHERE uuid = '{0}';
        """.format(uuid)
    dfq = dict_from_query(sql)
    project_id = dfq[0]['id']

    if project_owners:
        for person_uuid in project_owners:
            try:
                # get people id
                sql = """
                SELECT id from fabric_people WHERE uuid = '{0}';
                """.format(person_uuid)
                dfq = dict_from_query(sql)
                people_id = dfq[0]['id']

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

                # add cou to roles table
                cou = 'CO:COU:' + str(uuid) + '-po:members:active'
                sql = """
                INSERT INTO roles(people_id, role)
                VALUES ({0}, '{1}')
                ON CONFLICT ON CONSTRAINT roles_duplicate
                DO NOTHING
                """.format(people_id, cou)
                sql_list.append(sql)

                # add cou to roles table
                cou = 'CO:COU:' + str(uuid) + '-pm:members:active'
                sql = """
                INSERT INTO roles(people_id, role)
                VALUES ({0}, '{1}')
                ON CONFLICT ON CONSTRAINT roles_duplicate
                DO NOTHING
                """.format(people_id, cou)
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
        SELECT id from fabric_projects WHERE uuid = '{0}';
        """.format(uuid)
    dfq = dict_from_query(sql)
    project_id = dfq[0]['id']

    if tags:
        print(tags)
        for tag in tags:
            if len(tag) > 0:
                sql = """
                INSERT INTO tags(projects_id, tag)
                VALUES ({0}, '{1}')
                ON CONFLICT ON CONSTRAINT tags_duplicate
                DO NOTHING
                """.format(project_id, tag)
                sql_list.append(sql)

    commands = tuple(i for i in sql_list)
    print("[INFO] attempt to update tags data")
    run_sql_commands(commands)

    return projects_uuid_get(uuid)


def projects_create_post(name, description, facility=None, tags=None, project_owners=None,
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
    # create new project entry
    project_uuid = uuid4()
    project_cou = 'CO:COU:' + str(project_uuid)  + ':members:active'
    sql = """
    INSERT INTO fabric_projects(uuid, name, description, facility, cou)
    VALUES ('{0}', '{1}', '{2}', '{3}', '{4}');
    """.format(str(project_uuid), name, description, facility, project_cou)
    run_sql_commands(sql)

    sql_list = []
    # get project id
    sql = """
    SELECT id from fabric_projects WHERE uuid = '{0}';
    """.format(project_uuid)
    dfq = dict_from_query(sql)
    project_id = dfq[0]['id']

    if facility:
        sql = """
        UPDATE fabric_projects
        SET facility = '{0}'
        WHERE fabric_projects.id = {1};
        """.format(facility, project_id)
        sql_list.append(sql)

    # project leads
    # TODO

    # project owners
    if project_owners:
        for person_uuid in project_owners:
            try:
                # get people id
                sql = """
                SELECT id from fabric_people WHERE uuid = '{0}';
                """.format(person_uuid)
                dfq = dict_from_query(sql)
                people_id = dfq[0]['id']

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

                # add cou to roles table
                cou = 'CO:COU:' + str(project_uuid) + '-po:members:active'
                sql = """
                INSERT INTO roles(people_id, role)
                VALUES ({0}, '{1}')
                ON CONFLICT ON CONSTRAINT roles_duplicate
                DO NOTHING
                """.format(people_id, cou)
                sql_list.append(sql)

                # add cou to roles table
                cou = 'CO:COU:' + str(project_uuid) + '-pm:members:active'
                sql = """
                INSERT INTO roles(people_id, role)
                VALUES ({0}, '{1}')
                ON CONFLICT ON CONSTRAINT roles_duplicate
                DO NOTHING
                """.format(people_id, cou)
                sql_list.append(sql)

            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
                pass
    # project members
    if project_members:
        for person_uuid in project_members:
            try:
                # get people id
                sql = """
                SELECT id from fabric_people WHERE uuid = '{0}';
                """.format(person_uuid)
                dfq = dict_from_query(sql)
                people_id = dfq[0]['id']

                # add to project_members table
                sql = """
                INSERT INTO project_members(projects_id, people_id)
                VALUES ({0}, '{1}')
                ON CONFLICT ON CONSTRAINT project_members_duplicate
                DO NOTHING
                """.format(project_id, people_id)
                sql_list.append(sql)

                # add cou to roles table
                cou = 'CO:COU:' + str(project_uuid) + '-pm:members:active'
                sql = """
                INSERT INTO roles(people_id, role)
                VALUES ({0}, '{1}')
                ON CONFLICT ON CONSTRAINT roles_duplicate
                DO NOTHING
                """.format(people_id, cou)
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
                """.format(project_id, tag)
                sql_list.append(sql)

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
    SELECT id from fabric_projects WHERE uuid = '{0}';
    """.format(uuid)
    dfq = dict_from_query(sql)
    print(dfq)
    project_id = dfq[0]['id']

    # facility operators
    sql = """
    DELETE FROM facility_operators
    WHERE facility_operators.projects_id = {0};
    """.format(project_id)
    sql_list.append(sql)

    # project leads
    sql = """
    DELETE FROM project_leads
    WHERE project_leads.projects_id = {0};
    """.format(project_id)
    sql_list.append(sql)

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
    DELETE FROM roles
    WHERE roles.role LIKE '%{0}%';
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


def projects_get():  # noqa: E501
    """list of projects

    List of projects # noqa: E501


    :rtype: ProjectShort
    """
    # response as array of ProjectShort()
    response = []

    sql = """
    SELECT name, description, facility, uuid from fabric_projects
    ORDER BY name;
    """
    dfq = dict_from_query(sql)

    # construct response object
    for project in dfq:
        ps = ProjectShort()
        ps.name = project['name']
        ps.description = project['description']
        ps.facility = project['facility']
        ps.uuid = project['uuid']
        response.append(ps)

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
    sql_list = []
    # get project id
    sql = """
    SELECT id from fabric_projects WHERE uuid = '{0}';
    """.format(uuid)
    dfq = dict_from_query(sql)
    project_id = dfq[0]['id']

    if project_members:
        for person_uuid in project_members:
            try:
                # get people id
                sql = """
                SELECT id from fabric_people WHERE uuid = '{0}';
                """.format(person_uuid)
                dfq = dict_from_query(sql)
                people_id = dfq[0]['id']

                # remove people_id from project_members table
                sql = """
                DELETE FROM project_members
                WHERE project_members.projects_id = {0} AND project_members.people_id = {1};
                """.format(project_id, people_id)
                sql_list.append(sql)

                # remove cou from roles table
                cou = 'CO:COU:' + uuid + '-pm:members:active'
                sql = """
                DELETE FROM roles
                WHERE roles.people_id = {0} AND role = '{1}';
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
    SELECT id from fabric_projects WHERE uuid = '{0}';
    """.format(uuid)
    dfq = dict_from_query(sql)
    project_id = dfq[0]['id']

    if project_owners:
        for person_uuid in project_owners:
            try:
                # get people id
                sql = """
                    SELECT id from fabric_people WHERE uuid = '{0}';
                    """.format(person_uuid)
                dfq = dict_from_query(sql)
                people_id = dfq[0]['id']

                # remove people_id from project_owners table
                sql = """
                DELETE FROM project_owners
                WHERE project_owners.projects_id = {0} AND project_owners.people_id = {1};
                    """.format(project_id, people_id)
                sql_list.append(sql)

                # remove cou from roles table
                cou = 'CO:COU:' + uuid + '-pm:members:active'
                sql = """
                DELETE FROM roles
                WHERE roles.people_id = {0} AND role = '{1}';
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
    SELECT id from fabric_projects WHERE uuid = '{0}';
    """.format(uuid)
    dfq = dict_from_query(sql)
    project_id = dfq[0]['id']

    if tags:
        print(tags)
        for tag in tags:
            if len(tag) > 0:
                sql = """
                DELETE FROM tags
                WHERE tags.projects_id = {0} AND tags.tag = '{1}'
                """.format(project_id, tag)
                sql_list.append(sql)

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
    SELECT id from fabric_projects WHERE uuid = '{0}';
    """.format(uuid)
    dfq = dict_from_query(sql)
    project_id = dfq[0]['id']

    if name:
        sql = """
        UPDATE fabric_projects
        SET name = '{0}'
        WHERE fabric_projects.id = {1};
        """.format(name, project_id)
        sql_list.append(sql)
    if description:
        sql = """
        UPDATE fabric_projects
        SET description = '{0}'
        WHERE fabric_projects.id = {1};
        """.format(description, project_id)
        sql_list.append(sql)
    if facility:
        sql = """
        UPDATE fabric_projects
        SET facility = '{0}'
        WHERE fabric_projects.id = {1};
        """.format(facility, project_id)
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
    SELECT id from fabric_projects WHERE uuid = '{0}';
    """.format(uuid)
    dfq = dict_from_query(sql)
    project_id = dfq[0]['id']

    # get project attributes
    project_sql = """
    SELECT * from fabric_projects
    WHERE uuid = '{0}';
    """.format(uuid)
    project = dict_from_query(project_sql)[0]

    # facility-operators
    facility_operators = []
    fo_sql = """
    SELECT uuid from fabric_people
    WHERE fabric_people.is_facility_operator = TRUE
    ORDER BY uuid;
    """
    dfq = dict_from_query(fo_sql)
    for fo in dfq:
        facility_operators.append(fo['uuid'])

    # project-leads
    project_leads = []
    pl_sql = """
    SELECT uuid from fabric_people
    INNER JOIN project_leads ON fabric_people.id = project_leads.people_id 
    AND project_leads.projects_id = {0};
    """.format(project_id)
    dfq = dict_from_query(pl_sql)
    for pl in dfq:
        project_leads.append(pl['uuid'])

    # project-owners
    project_owners = []
    po_sql = """
    SELECT uuid from fabric_people
    INNER JOIN project_owners ON fabric_people.id = project_owners.people_id 
    AND project_owners.projects_id = {0};
    """.format(project_id)
    dfq = dict_from_query(po_sql)
    for po in dfq:
        project_owners.append(po['uuid'])

    # project-members
    project_members = []
    pm_sql = """
    SELECT uuid from fabric_people
    INNER JOIN project_members ON fabric_people.id = project_members.people_id 
    AND project_members.projects_id = {0};
    """.format(project_id)
    dfq = dict_from_query(pm_sql)
    for pm in dfq:
        project_members.append(pm['uuid'])

    # tags
    tags = []
    tags_sql = """
    SELECT tag from tags
    WHERE projects_id = {0}
    ORDER BY tag;
    """.format(project_id)
    dfq = dict_from_query(tags_sql)
    for tag in dfq:
        tags.append(tag['tag'])

    # construct response object
    response.name = project['name']
    response.description = project['description']
    response.facility = project['facility']
    response.uuid = project['uuid']
    response.facility_operators = facility_operators
    response.project_leads = project_leads
    response.project_owners = project_owners
    response.project_members = project_members
    response.tags = tags

    return response
