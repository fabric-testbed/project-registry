import re
from configparser import ConfigParser

from flask import request
from swagger_server.models.people_long import PeopleLong  # noqa: E501
from swagger_server.models.people_short import PeopleShort  # noqa: E501

from . import DEFAULT_USER_UUID
from .utils import dict_from_query, resolve_empty_people_uuid
from ..authorization.people import authorize_people_get, authorize_people_oidc_claim_sub_get, \
    authorize_people_uuid_get
from ..comanage_api.comanage_api import comanage_check_for_new_users

config = ConfigParser()
config.read('swagger_server/config/config.ini')

fabric_cou_set = {
    config.get('fabric-cou', 'fabric_active_users'),
    config.get('fabric-cou', 'facility_operators'),
    config.get('fabric-cou', 'project_leads')
}


def people_get(person_name=None):  # noqa: E501
    """list of people

    List of people # noqa: E501

    :param person_name: Search People by Name (ILIKE)
    :type person_name: str

    :rtype: List[PeopleShort]
    """
    # check authorization
    if not authorize_people_get(request.headers):
        return 'Authorization information is missing or invalid: /people', 401, \
               {'X-Error': 'Authorization information is missing or invalid'}

    # check for new comanage users
    if not comanage_check_for_new_users():
        return 'COmanage Error - Unable to retrieve co_people data', 500, \
               {'X-Error': 'Unable to retrieve co_people data'}

    # resolve any missing people uuids
    resolve_empty_people_uuid()

    # response as array of PeopleShort()
    response = []

    sql = """
    SELECT email, name, oidc_claim_sub, uuid FROM fabric_people
    """

    if person_name:
        sql = sql + """
        WHERE name ILIKE '%{}%'
        """.format(str(person_name))
        if not config.getboolean('mock', 'data'):
            sql = sql + """
            AND uuid != '{}'
            """.format(str(DEFAULT_USER_UUID))

    elif not config.getboolean('mock', 'data'):
        sql = sql + """
        WHERE uuid != '{}'
        """.format(str(DEFAULT_USER_UUID))

    sql = sql + """
    ORDER BY name;
    """
    dfq = dict_from_query(sql)

    # construct response object
    if dfq:
        for person in dfq:
            ps = PeopleShort()
            ps.email = person.get('email')
            ps.name = person.get('name')
            ps.uuid = person.get('uuid')
            response.append(ps)

    return response


def people_oidc_claim_sub_get(oidc_claim_sub):  # noqa: E501
    """person details by OIDC Claim sub

    Person details by OIDC Claim sub # noqa: E501

    :param oidc_claim_sub: Search People by OIDC Claim sub (exact match only)
    :type oidc_claim_sub: str

    :rtype: List[PeopleLong]
    """
    # resolve any missing people uuids
    resolve_empty_people_uuid()

    # get people uuid
    sql = """
    SELECT uuid from fabric_people WHERE oidc_claim_sub = '{0}'
    """.format(oidc_claim_sub)
    dfq = dict_from_query(sql)
    try:
        uuid = dfq[0].get('uuid')
    except IndexError or KeyError or TypeError as err:
        print(err)
        return 'OIDC Claim sub Not Found: {0}'.format(str(oidc_claim_sub)), 404, {'X-Error': 'OIDC Claim sub Not Found'}

    # check authorization
    if not authorize_people_oidc_claim_sub_get(request.headers, oidc_claim_sub):
        return 'Authorization information is missing or invalid: /people/oidc_claim_sub', 401, \
               {'X-Error': 'Authorization information is missing or invalid'}

    return people_uuid_get(uuid)


def people_uuid_get(uuid):  # noqa: E501
    """person details by UUID

    Person details by UUID # noqa: E501

    :param uuid: People identifier as UUID
    :type uuid: str

    :rtype: PeopleLong
    """
    # resolve any missing people uuids
    # resolve_empty_people_uuid()

    # response as PeopleLong()
    response = PeopleLong()

    # get people id
    sql = """
    SELECT id from fabric_people WHERE uuid = '{0}'
    """.format(uuid)
    dfq = dict_from_query(sql)
    try:
        people_id = dfq[0].get('id')
    except IndexError or KeyError or TypeError as err:
        print(err)
        return 'Person UUID Not Found: {0}'.format(str(uuid)), 404, {'X-Error': 'Person UUID Not Found'}

    # check authorization
    if not authorize_people_uuid_get(request.headers, uuid):
        return 'Authorization information is missing or invalid: /people/{uuid}', 401, \
               {'X-Error': 'Authorization information is missing or invalid'}

    # get person attributes
    sql_person = """
    SELECT oidc_claim_sub, email, name, uuid from fabric_people
    WHERE id = '{0}';
    """.format(people_id)
    person = dict_from_query(sql_person)[0]

    # get roles
    roles = []
    sql_roles = """
    SELECT role_name from fabric_roles
    WHERE people_id = '{0}';
    """.format(people_id)
    dfq = dict_from_query(sql_roles)
    for role in dfq:
        is_pr_role = role['role_name'] in fabric_cou_set or re.search(
            "([0-9|a-f]{8}-(?:[0-9|a-f]{4}-){3}[0-9|a-f]{12})", role['role_name'])
        if is_pr_role:
            roles.append(role['role_name'])

    # get projects
    projects = []
    if "CO:COU:facility-operators:members:active" in roles:
        # if is facility-operator, can access all projects (regardless of other roles)
        sql_projects = """
        SELECT uuid, name, description, facility, created_by from fabric_projects
        ORDER BY name;
        """
    else:
        # if not facility operator, get all groups from project owners and members tables
        sql_projects = """
        SELECT uuid, name, description, facility, created_by, created_time from fabric_projects
        INNER JOIN project_owners ON fabric_projects.id = project_owners.projects_id 
        AND project_owners.people_id = {0}
        UNION
        SELECT uuid, name, description, facility, created_by, created_time from fabric_projects
        INNER JOIN project_members ON fabric_projects.id = project_members.projects_id 
        AND project_members.people_id = {0}
        ORDER BY name;
        """.format(people_id)
    dfq = dict_from_query(sql_projects)
    for project in dfq:
        pr = {
            'uuid': project.get('uuid'), 'name': project.get('name'), 'description': project.get('description'),
            'facility': project.get('facility'), 'created_by': project.get('created_by'),
            'created_time': project.get('created_time')
        }
        projects.append(pr)

    # construct response object
    response.uuid = person.get('uuid')
    response.oidc_claim_sub = person.get('oidc_claim_sub')
    response.name = person.get('name')
    response.email = person.get('email')
    response.roles = roles
    response.projects = projects

    return response
