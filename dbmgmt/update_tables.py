#!/usr/bin/env python3
import json
import re
from configparser import ConfigParser
from datetime import datetime
from uuid import uuid4

import psycopg2
import requests
from drop_create_tables import Session
from pytz import timezone
from requests.auth import HTTPBasicAuth

config = ConfigParser()
config.read('../server/swagger_server/config/config.ini')

# COmanage API settings
CO_API_USERNAME = config.get('comanage-api', 'api_username')
CO_API_PASSWORD = config.get('comanage-api', 'api_key')
CO_API_COID = config.get('comanage-api', 'api_coid')
EMPTY_PARENT_FLAG = config.get('comanage-api', 'empty_parent_flag')

# Mock settings
MOCK_CO_PEOPLE_FILE = config.get('mock', 'mock_co_people')
MOCK_CO_PERSON_ROLES_FILE = config.get('mock', 'mock_co_person_roles')
MOCK_COUS_FILE = config.get('mock', 'mock_cous')
MOCK_EMAIL_ADDRESSES_FILE = config.get('mock', 'mock_email_addresses')
MOCK_NAMES_FILE = config.get('mock', 'mock_names')

# Timezone
TIMEZONE = 'America/New_York'

# default values
DEFAULT_NAME = 'INSERT_PROJECT_NAME'
DEFAULT_DESCRIPTION = 'INSERT_PROJECT_DESCRIPTION'
DEFAULT_FACILITY = 'INSERT_PROJECT_FACILITY'
DEFAULT_CREATED_BY = config.get('default-user', 'uuid')

default_user = {
    'co_person_id': config.get('default-user', 'co_person_id'),
    'co_status': config.get('default-user', 'co_status'),
    'email': config.get('default-user', 'email'),
    'name': config.get('default-user', 'name'),
    'oidc_claim_sub': config.get('default-user', 'oidc_claim_sub'),
    'role_names': str(config.get('default-user', 'roles')).split(' '),
    'uuid': config.get('default-user', 'uuid')
}


def insert_default_user():
    # SQL command
    command = """
    INSERT INTO fabric_people(co_id, co_person_id, co_status, email, name, oidc_claim_sub, uuid)
    VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')
    ON CONFLICT ON CONSTRAINT actor_identifier_duplicate
    DO NOTHING;
    """.format(CO_API_COID, default_user['co_person_id'], default_user['co_status'], default_user['email'],
               default_user['name'], default_user['oidc_claim_sub'], default_user['uuid'])
    print("[INFO] attempt to load co_person data: " + default_user['name'])
    run_sql_commands(command)

    # get fabric_people id
    sql = """
    SELECT id from fabric_people WHERE co_person_id = '{0}';
    """.format(default_user['co_person_id'])
    dfq = dict_from_query(sql)
    people_id = dfq[0].get('id')
    sql_list = []
    for role_name in default_user['role_names']:
        try:
            # get comanage_cous id and name
            sql = """
            SELECT id from comanage_cous WHERE name = '{0}';
            """.format(role_name)
            dfq = dict_from_query(sql)
            co_cou_id = dfq[0].get('id')
            command = """
            INSERT INTO fabric_roles(cou_id, people_id, role_name)
            VALUES ('{0}', '{1}', '{2}')
            ON CONFLICT ON CONSTRAINT fabric_role_duplicate
            DO NOTHING;
            """.format(co_cou_id, people_id, role_name)
            sql_list.append(command)
        except KeyError:
            pass
    commands = tuple(i for i in sql_list)
    print("[INFO] attempt to load roles:")
    run_sql_commands(commands)


def update_comanage_cou_data():
    if config.getboolean('mock', 'data'):
        print("[INFO] *** MOCK COU DATA ***")
        with open(MOCK_COUS_FILE, "r") as mock_cous:
            data = json.load(mock_cous)
            # pprint(data)
    else:
        response = requests.get(
            url='https://registry-test.cilogon.org/registry/cous.json',
            params={'coid': CO_API_COID},
            auth=HTTPBasicAuth(CO_API_USERNAME, CO_API_PASSWORD)
        )
        if response.status_code == requests.codes.ok:
            data = response.json()
        else:
            data = {'Cous': []}
    # update comanage_cous table based on findings
    sql_list = []
    for cou in data['Cous']:
        # collect all COUs found in FABRIC registry
        try:
            parent = cou['ParentId']
        except KeyError:
            parent = EMPTY_PARENT_FLAG
        command = """
        INSERT INTO comanage_cous(actor_identifier, co_id, cou_id, created_date, deleted, description, lft, 
        modified_date, name, parent_id, revision, rght, version)
        VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', '{11}', '{12}')
        ON CONFLICT ON CONSTRAINT cou_id_duplicate
        DO UPDATE 
        SET deleted = '{4}', description = '{5}', modified_date = '{7}', name = '{8}', revision = '{9}';
        """.format(cou['ActorIdentifier'], cou['CoId'], cou['Id'], cou['Created'], cou['Deleted'],
                   cou['Description'], cou['Lft'], cou['Modified'], cou['Name'], parent, cou['Revision'],
                   cou['Rght'], cou['Version'])
        sql_list.append(command)
    commands = tuple(i for i in sql_list)
    print("[INFO] attempt to load co_cou data: CoId = " + CO_API_COID)
    run_sql_commands(commands)


def update_comanage_people_data():
    if config.getboolean('mock', 'data'):
        print("[INFO] *** MOCK CO_PEOPLE DATA ***")
        with open(MOCK_CO_PEOPLE_FILE, "r") as mock_co_people:
            people_data = json.load(mock_co_people)
            # pprint(people_data)
    else:
        response = requests.get(
            url='https://registry-test.cilogon.org/registry/co_people.json',
            params={'coid': CO_API_COID},
            auth=HTTPBasicAuth(CO_API_USERNAME, CO_API_PASSWORD)
        )
        if response.status_code == requests.codes.ok:
            people_data = response.json()
        else:
            print(response)
            people_data = {'CoPeople': []}
    # update project_people table based on findings
    for person in people_data['CoPeople']:
        if person['Status'] == 'Active':
            # get name
            if config.getboolean('mock', 'data'):
                name_data = {'Names': [{'Given': '', 'Middle': '', 'Family': '', 'Suffix': ''}]}
                with open(MOCK_NAMES_FILE, "r") as mock_names:
                    all_name_data = json.load(mock_names)
                    for item in all_name_data:
                        if item['Names'][0]['Person']['Id'] == person['Id']:
                            name_data = item
                            break
            else:
                response = requests.get(
                    url='https://registry-test.cilogon.org/registry/names.json',
                    params={'copersonid': person['Id'], 'coid': CO_API_COID},
                    auth=HTTPBasicAuth(CO_API_USERNAME, CO_API_PASSWORD)
                )
                if response.status_code == requests.codes.ok:
                    name_data = response.json()
                else:
                    print(response)
                    name_data = {'Names': [{'Given': '', 'Middle': '', 'Family': '', 'Suffix': ''}]}
            # get email
            if config.getboolean('mock', 'data'):
                email_data = {'EmailAddresses': [{'Mail': ''}]}
                with open(MOCK_EMAIL_ADDRESSES_FILE, "r") as mock_email_addresses:
                    all_email_data = json.load(mock_email_addresses)
                    for item in all_email_data:
                        if item['EmailAddresses'][0]['Person']['Id'] == person['Id']:
                            email_data = item
                            break
            else:
                response = requests.get(
                    url='https://registry-test.cilogon.org/registry/email_addresses.json',
                    params={'copersonid': person['Id'], 'coid': CO_API_COID},
                    auth=HTTPBasicAuth(CO_API_USERNAME, CO_API_PASSWORD)
                )
                if response.status_code == requests.codes.ok:
                    email_data = response.json()
                else:
                    print(response)
                    email_data = {'EmailAddresses': [{'Mail': ''}]}
            # set person attributes for database
            co_id = person['CoId']
            co_person_id = person['Id']
            co_status = person['Status']
            email = email_data['EmailAddresses'][0]['Mail']
            name = name_data['Names'][0]['Given']
            if name_data['Names'][0]['Middle']:
                name = name + ' ' + name_data['Names'][0]['Middle']
            if name_data['Names'][0]['Family']:
                name = name + ' ' + name_data['Names'][0]['Family']
            if name_data['Names'][0]['Suffix']:
                name = name + ', ' + name_data['Names'][0]['Suffix']
            oidc_claim_sub = person['ActorIdentifier']
            # check UIS API mock settings
            if config.getboolean('mock', 'uis_api'):
                uuid = uuid4()
            else:
                uuid = ''
            # SQL command
            command = """
            INSERT INTO fabric_people(co_id, co_person_id, co_status, email, name, oidc_claim_sub, uuid)
            VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')
            ON CONFLICT ON CONSTRAINT actor_identifier_duplicate
            DO NOTHING;
            """.format(co_id, co_person_id, co_status, email, name, oidc_claim_sub, uuid)
            print("[INFO] attempt to load co_person data: " + name)
            run_sql_commands(command)
            update_co_person_cou_links(co_person_id)
        else:
            # TODO: do we want to track CO_PEOPLE that are not "Active"?
            pass


def update_co_person_cou_links(co_person_id):
    # get roles
    if config.getboolean('mock', 'data'):
        role_data = {'CoPersonRoles': []}
        with open(MOCK_CO_PERSON_ROLES_FILE, "r") as mock_co_person_roles:
            all_role_data = json.load(mock_co_person_roles)
            for item in all_role_data:
                if item['CoPersonRoles'][0]['Person']['Id'] == co_person_id:
                    role_data = item
                    break
    else:
        response = requests.get(
            url='https://registry-test.cilogon.org/registry/co_person_roles.json',
            params={'copersonid': co_person_id, 'coid': CO_API_COID},
            auth=HTTPBasicAuth(CO_API_USERNAME, CO_API_PASSWORD)
        )
        if response.status_code == requests.codes.ok:
            role_data = response.json()
        else:
            print(response)
            role_data = {'CoPersonRoles': []}
    # get fabric_people id
    sql = """
    SELECT id from fabric_people WHERE co_person_id = '{0}'
    """.format(co_person_id)
    dfq = dict_from_query(sql)
    people_id = dfq[0].get('id')
    sql_list = []
    for role in role_data['CoPersonRoles']:
        try:
            # get comanage_cous id and name
            sql = """
            SELECT id, name from comanage_cous WHERE cou_id = '{0}'
            """.format(role['CouId'])
            dfq = dict_from_query(sql)
            co_cou_id = dfq[0].get('id')
            co_role_name = dfq[0].get('name')
            command = """
            INSERT INTO fabric_roles(cou_id, people_id, role_name)
            VALUES ('{0}', '{1}', '{2}')
            ON CONFLICT ON CONSTRAINT fabric_role_duplicate
            DO NOTHING;
            """.format(co_cou_id, people_id, co_role_name)
            sql_list.append(command)
        except KeyError:
            pass
    commands = tuple(i for i in sql_list)
    print("[INFO] attempt to load roles:")
    run_sql_commands(commands)


def update_projects_data():
    cous = []
    sql = """
    SELECT name from comanage_cous;
    """
    dfq = dict_from_query(sql)
    for cou in dfq:
        cous.append(cou['name'])
    # update fabric_projects table
    sql_list = []
    temp_list = []
    for cou in cous:
        match = re.search("([0-9|a-f]{8}-(?:[0-9|a-f]{4}-){3}[0-9|a-f]{12})", cou)
        if match:
            temp_list.append(match[0])
    cou_list = set(temp_list)
    for cou in cou_list:
        t_now = datetime.now()
        t_zone = timezone(TIMEZONE)
        created_time = t_zone.localize(t_now)
        command = """
        INSERT INTO fabric_projects(uuid, name, description, facility, created_by, created_time)
        VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}')
        ON CONFLICT ON CONSTRAINT projects_uuid
        DO NOTHING;
        """.format(cou, DEFAULT_NAME, DEFAULT_DESCRIPTION, DEFAULT_FACILITY, DEFAULT_CREATED_BY, created_time)
        sql_list.append(command)
    commands = tuple(i for i in sql_list)
    print("[INFO] attempt to load project data")
    run_sql_commands(commands)

    # update project_owners and project_members tables
    sql_list = []
    sql = """
    SELECT people_id, role_name 
    FROM fabric_roles
    WHERE regexp_match(role_name, '([0-9|a-f]{8}-(?:[0-9|a-f]{4}-){3}[0-9|a-f]{12}-p[m|o])') IS NOT NULL;
    """
    role_dict = dict_from_query(sql)
    for role in role_dict:
        if role['role_name'][-3:] == '-po':
            print('[INFO] project owners role: ' + role['role_name'])
            sql = """
            SELECT id FROM fabric_projects WHERE uuid = '{0}';
            """.format(role['role_name'][:-3])
            dfq = dict_from_query(sql)

            command = """
            INSERT INTO project_owners(projects_id, people_id)
            VALUES ('{0}', '{1}')
            ON CONFLICT ON CONSTRAINT project_owners_duplicate
            DO NOTHING;
            """.format(int(dfq[0]['id']), int(role['people_id']))
            sql_list.append(command)

        elif role['role_name'][-3:] == '-pm':
            print('[INFO] project members role: ' + role['role_name'])
            sql = """
            SELECT id FROM fabric_projects WHERE uuid = '{0}';
            """.format(role['role_name'][:-3])
            dfq = dict_from_query(sql)

            command = """
            INSERT INTO project_members(projects_id, people_id)
            VALUES ('{0}', '{1}')
            ON CONFLICT ON CONSTRAINT project_members_duplicate
            DO NOTHING;
            """.format(int(dfq[0]['id']), int(role['people_id']))
            sql_list.append(command)

    commands = tuple(i for i in sql_list)
    print("[INFO] attempt to load roles data")
    run_sql_commands(commands)


def dict_from_query(query=None):
    session = Session()
    resultproxy = session.execute(query)
    session.close()

    d, a = {}, []
    for rowproxy in resultproxy:
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for column, value in rowproxy.items():
            # build up the dictionary
            d = {**d, **{column: value}}
        a.append(d)

    return a


def run_sql_commands(commands):
    """ create tables in the PostgreSQL database"""
    session = Session()
    try:
        if isinstance(commands, tuple):
            for command in commands:
                session.execute(command)
        else:
            session.execute(commands)
        session.commit()
        print("[INFO] data loaded successfully!")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if session is not None:
            session.close()


def load_version_data():
    commands = (
        """
        INSERT INTO version(id, version, gitsha1)
        VALUES (1, '1.0.0', 'd943bb9fd09e00a2fc672df344a087e8dd89ffb0')
        ON CONFLICT (id)
        DO UPDATE SET version = Excluded.version, gitsha1 = Excluded.gitsha1
        """
    )
    print("[INFO] attempt to load version data")
    run_sql_commands(commands)


if __name__ == '__main__':
    if config.getboolean('mock', 'data'):
        print("[INFO] *** USING MOCK DATA ***")

    load_version_data()
    update_comanage_cou_data()
    insert_default_user()
    update_comanage_people_data()
    update_projects_data()
