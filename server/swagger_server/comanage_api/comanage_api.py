import json
from configparser import ConfigParser
from pprint import pprint

import requests
from requests.auth import HTTPBasicAuth

from . import EMPTY_PARENT_FLAG, CO_API_COID, PARENT_COU_ID, CO_API_PASSWORD, CO_API_USERNAME, MOCK_ROLE_ID_FLAG
from .mock_comanage_api import mock_comanage_add_new_cou, mock_comanage_remove_cou, mock_comanange_add_users_to_cou, \
    mock_comanage_remove_users_from_cou
from ..response_code.utils import run_sql_commands, dict_from_query

config = ConfigParser()
config.read('swagger_server/config/config.ini')


def comanage_projects_add_members_put(project_uuid, project_members):
    # get project cou
    project_cou_pm = str(project_uuid) + '-pm'
    # get co_cou_id
    sql = """
    SELECT id, cou_id from comanage_cous WHERE name = '{0}';
    """.format(project_cou_pm)
    try:
        dfq = dict_from_query(sql)
        cou_id = dfq[0].get('id')
        co_cou_id = dfq[0].get('cou_id')
    except KeyError or IndexError as err:
        print(err)
        return False
    for user_uuid in project_members:
        # get co_person_id
        sql = """
       SELECT id, co_person_id from fabric_people WHERE uuid = '{0}';
       """.format(user_uuid)
        try:
            dfq = dict_from_query(sql)
            person_id = dfq[0].get('id')
            co_person_id = dfq[0].get('co_person_id')
            co_role_id = comanange_add_users_to_cou(co_person_id, co_cou_id)
        except KeyError or IndexError as err:
            print(err)
            return False
        # add cou to fabric_roles table
        command = """
        INSERT INTO fabric_roles(cou_id, people_id, role_name, role_id)
        VALUES ({0}, {1}, '{2}', {3})
        ON CONFLICT ON CONSTRAINT fabric_role_duplicate
        DO NOTHING;
        """.format(int(cou_id), int(person_id), project_cou_pm, int(co_role_id))
        run_sql_commands(command)

    return True


def comanage_projects_add_owners_put(project_uuid, project_owners):
    # get project cou
    project_cou_po = str(project_uuid) + '-po'
    # get co_cou_id
    sql = """
    SELECT id, cou_id from comanage_cous WHERE name = '{0}';
    """.format(project_cou_po)
    try:
        dfq = dict_from_query(sql)
        cou_id = dfq[0].get('id')
        co_cou_id = dfq[0].get('cou_id')
    except KeyError or IndexError as err:
        print(err)
        return False
    for user_uuid in project_owners:
        # get co_person_id
        sql = """
       SELECT id, co_person_id from fabric_people WHERE uuid = '{0}';
       """.format(user_uuid)
        try:
            dfq = dict_from_query(sql)
            person_id = dfq[0].get('id')
            co_person_id = dfq[0].get('co_person_id')
            co_role_id = comanange_add_users_to_cou(co_person_id, co_cou_id)
        except KeyError or IndexError as err:
            print(err)
            return False
        # add cou to fabric_roles table
        command = """
        INSERT INTO fabric_roles(cou_id, people_id, role_name, role_id)
        VALUES ({0}, {1}, '{2}', {3})
        ON CONFLICT ON CONSTRAINT fabric_role_duplicate
        DO NOTHING;
        """.format(int(cou_id), int(person_id), project_cou_po, int(co_role_id))
        run_sql_commands(command)

    return True


def comanage_projects_create_post(project_uuid, project_name):
    project_cou_po = str(project_uuid) + '-po'
    project_cou_pm = str(project_uuid) + '-pm'
    cous_to_add = [project_cou_po, project_cou_pm]
    for cou_name in cous_to_add:
        cou = comanage_add_new_cou(cou_name, project_name)['Cous'][0]
        try:
            parent_id = cou['ParentId']
        except IndexError or KeyError or TypeError as err:
            print(err)
            parent_id = EMPTY_PARENT_FLAG

        command = """
        INSERT INTO comanage_cous(actor_identifier, co_id, created_date, deleted, description, 
        cou_id, lft, modified_date, name, parent_id, revision, rght, version)
        VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', '{11}', '{12}')
        ON CONFLICT ON CONSTRAINT cou_id_duplicate
        DO UPDATE 
        SET deleted = '{3}', description = '{4}', modified_date = '{7}', name = '{8}', revision = '{10}';
        """.format(cou['ActorIdentifier'], cou['CoId'], cou['Created'], cou['Deleted'], cou['Description'],
                   cou['Id'], cou['Lft'], cou['Modified'], cou['Name'], parent_id, cou['Revision'],
                   cou['Rght'], cou['Version'])
        run_sql_commands(command)

    return True


def comanage_projects_delete_delete(project_uuid):
    project_cou_po = str(project_uuid) + '-po'
    project_cou_pm = str(project_uuid) + '-pm'
    cous_to_remove = [project_cou_po, project_cou_pm]
    for cou in cous_to_remove:
        sql = """
        SELECT cou_id FROM comanage_cous WHERE name = '{0}';
        """.format(cou)
        dfq = dict_from_query(sql)
        cou_id = dfq[0].get('cou_id')
        if comanage_remove_cou(cou_id):
            command = """
            DELETE FROM comanage_cous WHERE cou_id = {0};
            """.format(cou_id)
            run_sql_commands(command)
        else:
            print('[INFO] error at: comanage_projects_delete_delete(project_uuid)')
            return False
    return True


def comanage_projects_remove_members_put(project_uuid, project_members):
    # get project cou
    project_cou_pm = str(project_uuid) + '-pm'
    for user_uuid in project_members:
        # get people_id
        sql = """
        SELECT id FROM fabric_people WHERE uuid = '{0}';
        """.format(user_uuid)
        try:
            people_id = dict_from_query(sql)[0].get('id')
        except IndexError or KeyError as err:
            print(err)
            return False
        # get co_role_id
        sql = """
        SELECT role_id FROM fabric_roles  
        WHERE people_id = {0}
        AND role_name = '{1}';
        """.format(people_id, project_cou_pm)
        try:
            co_role_id = dict_from_query(sql)[0].get('role_id')
            co_role_removed = comanage_remove_users_from_cou(co_role_id)
        except IndexError or KeyError as err:
            print(err)
            return False
        if co_role_removed:
            # remove cou to fabric_roles table
            command = """
            DELETE FROM fabric_roles
            WHERE people_id = {0} AND role_name = '{1}';
            """.format(int(people_id), project_cou_pm)
            run_sql_commands(command)
        else:
            print('[INFO] error at: comanage_projects_remove_members_put(project_uuid, project_members)')

    return True


def comanage_projects_remove_owners_put(project_uuid, project_owners):
    # get project cou
    project_cou_po = str(project_uuid) + '-po'
    for user_uuid in project_owners:
        # get people_id
        sql = """
        SELECT id FROM fabric_people WHERE uuid = '{0}';
        """.format(user_uuid)
        try:
            people_id = dict_from_query(sql)[0].get('id')
        except IndexError or KeyError as err:
            print(err)
            return False
        # get co_role_id
        sql = """
        SELECT role_id FROM fabric_roles  
        WHERE people_id = {0}
        AND role_name = '{1}';
        """.format(people_id, project_cou_po)
        try:
            co_role_id = dict_from_query(sql)[0].get('role_id')
            co_role_removed = comanage_remove_users_from_cou(co_role_id)
        except IndexError or KeyError as err:
            print(err)
            return False
        if co_role_removed:
            # remove cou to fabric_roles table
            command = """
            DELETE FROM fabric_roles
            WHERE people_id = {0} AND role_name = '{1}';
            """.format(int(people_id), project_cou_po)
            run_sql_commands(command)
        else:
            print('[INFO] error at: comanage_projects_remove_owners_put(project_uuid, project_owners)')

    return True


def comanage_add_new_cou(cou_name, cou_description):
    # ref: https://spaces.at.internet2.edu/display/COmanage/COU+API
    # example COU request object format:
    # {
    #   "RequestType":"Cous",
    #   "Version":"1.0",
    #   "Cous":
    #   [
    #     {
    #       "Version":"1.0",
    #       "CoId":"5",
    #       "ParentId":"14",
    #       "Name":"Undulator Team",
    #       "Description":"Undulator Team"
    #     }
    #   ]
    # }
    # example COU 201 created response object format:
    # {
    #     "ResponseType": "NewObject",
    #     "Version": "1.0",
    #     "ObjectType": "Cou",
    #     "Id": "181"
    # }

    if config.getboolean('mock', 'comanage_api'):
        cou_data = mock_comanage_add_new_cou(cou_name, cou_description)
    else:
        cou_request = json.dumps({
            'RequestType': 'Cous',
            'Version': '1.0',
            'Cous':
                [
                    {
                        'Version': '1.0',
                        'CoId': CO_API_COID,
                        'ParentId': PARENT_COU_ID,
                        'Name': cou_name,
                        'Description': cou_description
                    }
                ]
        })
        response = requests.post(
            url='https://registry-test.cilogon.org/registry/cous.json',
            data=cou_request,
            auth=HTTPBasicAuth(CO_API_USERNAME, CO_API_PASSWORD)
        )
        if response.status_code == requests.codes.created:
            new_cou = response.json()
        else:
            print(response)
            new_cou = {
                'ResponseType': 'NewObject',
                "Version": '1.0',
                'ObjectType': 'Cou',
                'Id': EMPTY_PARENT_FLAG
            }

        if new_cou.get('Id') == EMPTY_PARENT_FLAG:
            cou_data = {'Cous': []}
        else:
            response = requests.get(
                url="https://registry-test.cilogon.org/registry/cous/{0}.json".format(new_cou.get('Id')),
                params={'coid': CO_API_COID},
                auth=HTTPBasicAuth(CO_API_USERNAME, CO_API_PASSWORD)
            )
            if response.status_code == requests.codes.ok:
                cou_data = response.json()
            else:
                cou_data = {'Cous': []}

    return cou_data


def comanage_remove_cou(cou_id):
    # ref: https://spaces.at.internet2.edu/display/COmanage/COU+API
    if config.getboolean('mock', 'comanage_api'):
        return mock_comanage_remove_cou(cou_id)
    else:
        response = requests.delete(
            url="https://registry-test.cilogon.org/registry/cous/{0}.json".format(cou_id),
            auth=HTTPBasicAuth(CO_API_USERNAME, CO_API_PASSWORD)
        )
        if response.status_code == requests.codes.ok:
            return True
        else:
            print(response)
            return False


def comanange_add_users_to_cou(co_person_id, co_cou_id):
    # ref: https://spaces.at.internet2.edu/display/COmanage/CoPersonRole+API
    if config.getboolean('mock', 'comanage_api'):
        new_co_person_role = mock_comanange_add_users_to_cou(co_person_id, co_cou_id)
    else:
        co_person_role_request = json.dumps({
            'RequestType': 'CoPersonRoles',
            'Version': '1.0',
            'CoPersonRoles':
                [
                    {
                        'Version': '1.0',
                        'Person':
                            {
                                'Type': 'CO',
                                'Id': co_person_id
                            },
                        'CouId': co_cou_id,
                        'Affiliation': 'member',
                        'Title': '',
                        'O': 'Fabric',
                        'Ordr': '',
                        'Ou': '',
                        'Status': 'Active'
                    }
                ]
        })
        response = requests.post(
            url='https://registry-test.cilogon.org/registry/co_person_roles.json',
            params={'coid': '{0}'.format(CO_API_COID)},
            data=co_person_role_request,
            auth=HTTPBasicAuth(CO_API_USERNAME, CO_API_PASSWORD)
        )
        if response.status_code == requests.codes.created:
            new_co_person_role = response.json()
        else:
            print(response)
            new_co_person_role = {
                'ResponseType': 'NewObject',
                'Version': '1.0',
                'ObjectType': 'CoPersonRole',
                'Id': MOCK_ROLE_ID_FLAG
            }

    return new_co_person_role.get('Id')


def comanage_remove_users_from_cou(role_id):
    # ref: https://spaces.at.internet2.edu/display/COmanage/CoPersonRole+API
    if config.getboolean('mock', 'comanage_api'):
        return mock_comanage_remove_users_from_cou(role_id)
    else:
        response = requests.delete(
            url='https://registry-test.cilogon.org/registry/co_person_roles/{0}.json'.format(str(role_id)),
            auth=HTTPBasicAuth(CO_API_USERNAME, CO_API_PASSWORD)
        )
        if response.status_code == requests.codes.ok:
            return True
        else:
            print(response)
            return False
