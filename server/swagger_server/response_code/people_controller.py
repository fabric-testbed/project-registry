from swagger_server.models.people_long import PeopleLong  # noqa: E501
from swagger_server.models.people_short import PeopleShort  # noqa: E501

from .utils import dict_from_query


def people_get():  # noqa: E501
    """list of people

    list of people # noqa: E501


    :rtype: List[PeopleShort]
    """
    # response as array of PeopleShort()
    response = []

    sql = """
    SELECT email, name, uuid from fabric_people
    ORDER BY name;
    """
    dfq = dict_from_query(sql)

    # construct response object
    for person in dfq:
        ps = PeopleShort()
        ps.email = person['email']
        ps.name = person['name']
        ps.uuid = person['uuid']
        response.append(ps)

    return response


def people_uuid_get(uuid):  # noqa: E501
    """person details

    Person details # noqa: E501

    :param uuid: People identifier as UUID
    :type uuid: str

    :rtype: PeopleLong
    """
    # response as PeopleLong()
    response = PeopleLong()

    # get people id
    sql = """
    SELECT id from fabric_people WHERE uuid = '{0}'
    """.format(uuid)
    dfq = dict_from_query(sql)
    people_id = dfq[0]['id']

    # get person attributes
    sql_person = """
    SELECT cilogon_id, email, eppn, name, uuid from fabric_people
    WHERE id = '{0}';
    """.format(people_id)
    person = dict_from_query(sql_person)[0]

    # get roles
    roles = []
    sql_roles = """
    SELECT role from roles
    WHERE people_id = '{0}';
    """.format(people_id)
    dfq = dict_from_query(sql_roles)
    for role in dfq:
        roles.append(role['role'])

    # get projects
    projects = []
    if "CO:COU:facility-operators:members:active" in roles:
        # if is facility-operator, can access all projects (regardless of other roles)
        sql_projects = """
        SELECT uuid from fabric_projects
        ORDER BY uuid;
        """
    else:
        # if not facility operator, get all groups from project leads, owners and members tables
        sql_projects = """
        SELECT uuid from fabric_projects
        INNER JOIN project_leads ON fabric_projects.id = project_leads.projects_id 
        AND project_leads.people_id = {0}
        UNION
        SELECT uuid from fabric_projects
        INNER JOIN project_owners ON fabric_projects.id = project_owners.projects_id 
        AND project_owners.people_id = {0}
        UNION
        SELECT uuid from fabric_projects
        INNER JOIN project_members ON fabric_projects.id = project_members.projects_id 
        AND project_members.people_id = {0}
        """.format(people_id)
    dfq = dict_from_query(sql_projects)
    for project in dfq:
        projects.append(project['uuid'])

    # construct response object
    response.uuid = person['uuid']
    response.cilogon_id = person['cilogon_id']
    response.name = person['name']
    response.email = person['email']
    response.eppn = person['eppn']
    response.roles = roles
    response.projects = projects

    return response
