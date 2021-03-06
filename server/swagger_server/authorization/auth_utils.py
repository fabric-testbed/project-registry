import re
from configparser import ConfigParser

from jwt import decode

from ..models.people_long import PeopleLong

config = ConfigParser()
config.read('swagger_server/config/config.ini')

fabric_cou_set = {
    config.get('fabric-cou', 'fabric_active_users'),
    config.get('fabric-cou', 'facility_operators'),
    config.get('fabric-cou', 'project_leads')
}

# set default user uuid flag
DEFAULT_USER_OIDC_CLAIM_SUB = config.get('default-user', 'oidc_claim_sub')


def get_api_person(x_vouch_idp_idtoken):
    api_user = PeopleLong()
    if config.getboolean('mock', 'data'):
        api_user = auth_utils_oidc_claim_sub_get(DEFAULT_USER_OIDC_CLAIM_SUB)
    elif x_vouch_idp_idtoken:
        # print(x_vouch_idp_idtoken)
        decoded = decode(x_vouch_idp_idtoken, verify=False)
        try:
            api_user = auth_utils_oidc_claim_sub_get(decoded.get('sub'))
            # print(api_user)
        except IndexError or KeyError or TypeError as err:
            print(err)
            print('User not found')
    else:
        api_user = auth_utils_oidc_claim_sub_get(config.get('default-user', 'oidc_claim_sub'))
    print('[INFO] Operating as: ' + str(api_user.name))
    return api_user


def auth_utils_oidc_claim_sub_get(oidc_claim_sub):  # noqa: E501
    from ..response_code.utils import dict_from_query
    # response as PeopleLong()
    response = PeopleLong()

    # get people uuid
    sql = """
    SELECT id from fabric_people WHERE oidc_claim_sub = '{0}'
    """.format(oidc_claim_sub)
    dfq = dict_from_query(sql)
    if dfq:
        try:
            people_id = dfq[0].get('id')
        except IndexError or KeyError or TypeError as err:
            print(err)
            # user not found within COmanage - return default user
            api_user = auth_utils_oidc_claim_sub_get(config.get('default-user', 'oidc_claim_sub'))
            return api_user
    else:
        return None

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
        SELECT uuid, name, description, facility, created_by from fabric_projects
        INNER JOIN project_owners ON fabric_projects.id = project_owners.projects_id 
        AND project_owners.people_id = {0}
        UNION
        SELECT uuid, name, description, facility, created_by from fabric_projects
        INNER JOIN project_members ON fabric_projects.id = project_members.projects_id 
        AND project_members.people_id = {0}
        ORDER BY name;
        """.format(people_id)
    dfq = dict_from_query(sql_projects)
    for project in dfq:
        pr = {'uuid': project.get('uuid'), 'name': project.get('name'), 'description': project.get('description'),
              'facility': project.get('facility'), 'created_by': project.get('created_by')}
        projects.append(pr)

    # construct response object
    response.uuid = person.get('uuid')
    response.oidc_claim_sub = person.get('oidc_claim_sub')
    response.name = person.get('name')
    response.email = person.get('email')
    if person.get('eppn') != 'None':
        response.eppn = person.get('eppn')
    else:
        response.eppn = ''
    response.roles = roles
    response.projects = projects

    return response
