import re
from configparser import ConfigParser
from pprint import pprint

from flask import request
from swagger_server.models.people_long import PeopleLong  # noqa: E501
from swagger_server.models.people_short import PeopleShort  # noqa: E501

from . import DEFAULT_USER_UUID
from .utils import dict_from_query, resolve_empty_people_uuid, run_sql_commands, cors_response
from ..authorization.people import authorize_people_get, authorize_people_oidc_claim_sub_get, \
    authorize_people_uuid_get, authorize_people_role_attribute_sync_get
from ..comanage_api.comanage_api import comanage_check_for_new_users, comanage_people_role_attribute_sync_get

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
        return cors_response(
            request=request,
            status_code=401,
            body='Authorization information is missing or invalid: /people',
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
        return cors_response(
            request=request,
            status_code=401,
            body='Authorization information is missing or invalid: /people/oidc_claim_sub',
            x_error='Authorization information is missing or invalid'
        )

    return people_uuid_get(uuid)


def people_role_attribute_sync_get():  # noqa: E501
    """role attribute sync

    Synchronize COU Role Attributes # noqa: E501


    :rtype: None
    """

    # check authorization
    authorized, api_person = authorize_people_role_attribute_sync_get(request.headers)
    if not authorized:
        return cors_response(
            request=request,
            status_code=401,
            body='Authorization information is missing or invalid: /people',
            x_error='Authorization information is missing or invalid'
        )

    sql = """
    SELECT id, co_person_id FROM fabric_people
    WHERE oidc_claim_sub = '{0}';
    """.format(api_person.oidc_claim_sub)
    dfq = dict_from_query(sql)
    try:
        co_person_id = dfq[0].get('co_person_id')
        person_id = dfq[0].get('id')
    except IndexError or KeyError as err:
        print(err)
        co_person_id = -1
        person_id = -1
    co_person_roles = comanage_people_role_attribute_sync_get(co_person_id)
    # add new roles from comanage to pr
    co_role_id_list = []
    for role in co_person_roles:
        role_id = role.get('Id')
        co_role_id_list.append(int(role_id))
        sql = """
        SELECT EXISTS (
            SELECT 1 FROM fabric_roles
            WHERE people_id = {0} AND role_id = {1}
        );
        """.format(person_id, role_id)
        dfq = dict_from_query(sql)
        if not dfq[0].get('exists') and role.get('CouId'):
            sql = """
            SELECT id, name FROM comanage_cous
            WHERE cou_id = {0};
            """.format(role.get('CouId'))
            dfq = dict_from_query(sql)
            try:
                cou_id = dfq[0].get('id')
                role_name = dfq[0].get('name')
            except IndexError or KeyError as err:
                print(err)
                cou_id = -1
                role_name = None
            print("[INFO] Adding role: people_id = {0}, cou_id = {1}, role_id = {2}, role_name = {3}".format(
                str(person_id), str(cou_id), str(role_id), str(role_name)
            ))
            # add cou to fabric_roles table
            command = """
            INSERT INTO fabric_roles(people_id, cou_id, role_id, role_name)
            VALUES ({0}, {1}, {2}, '{3}')
            ON CONFLICT ON CONSTRAINT fabric_role_duplicate
            DO NOTHING;
            """.format(int(person_id), int(cou_id), int(role_id), str(role_name))
            run_sql_commands(command)


    # remove stale roles from pr not found in comanage
    sql = """
    SELECT role_id FROM fabric_roles
    WHERE people_id = {0};
    """.format(person_id)
    dfq = dict_from_query(sql)
    pr_role_id_list = []
    try:
        for item in dfq:
            pr_role_id_list.append(item.get('role_id'))
    except IndexError or KeyError as err:
        print(err)
    for role in pr_role_id_list:
        if role not in co_role_id_list:
            print("[INFO] Removing role: people_id = {0}, role_id = {1}".format(
                str(person_id), str(role)
            ))
            # remove cou to fabric_roles table
            command = """
            DELETE FROM fabric_roles
            WHERE people_id = {0} AND role_id = {1};
            """.format(int(person_id), int(role))
            run_sql_commands(command)

    print("[DEBUG] CO roles: {0}".format(co_role_id_list))
    print("[DEBUG] PR roles: {0}".format(pr_role_id_list))

    return cors_response(
        request=request,
        status_code=200,
        body='Role attribute sync'
    )


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
        return cors_response(
            request=request,
            status_code=404,
            body='Person UUID Not Found: {0}'.format(str(uuid)),
            x_error='Person UUID Not Found'
        )

    # check authorization
    if not authorize_people_uuid_get(request.headers, uuid):
        return cors_response(
            request=request,
            status_code=401,
            body='Authorization information is missing or invalid: /people/{uuid}',
            x_error='Authorization information is missing or invalid'
        )

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
