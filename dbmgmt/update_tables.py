#!/usr/bin/env python3
import json
import re
import os
from configparser import ConfigParser
from pprint import pprint
from uuid import uuid4

import psycopg2
import requests
from requests.auth import HTTPBasicAuth

from drop_create_tables import Session

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
MOCK_ROLE_ID_FLAG = config.get('mock', 'mock_role_id_flag')

# Timezone
TIMEZONE = 'UTC'

# default values
DEFAULT_NAME = 'INSERT_PROJECT_NAME'
DEFAULT_DESCRIPTION = 'INSERT_PROJECT_DESCRIPTION'
DEFAULT_FACILITY = 'FABRIC'
DEFAULT_CREATED_BY = config.get('default-user', 'uuid')

# default user
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
            role_id = MOCK_ROLE_ID_FLAG
            # get comanage_cous id and name
            sql = """
            SELECT id from comanage_cous WHERE name = '{0}';
            """.format(role_name)
            dfq = dict_from_query(sql)
            co_cou_id = dfq[0].get('id')
            command = """
            INSERT INTO fabric_roles(cou_id, people_id, role_name, role_id)
            VALUES ({0}, {1}, '{2}', {3})
            ON CONFLICT ON CONSTRAINT fabric_role_duplicate
            DO NOTHING;
            """.format(int(co_cou_id), int(people_id), role_name, int(role_id))
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
            print("[ERROR] unable to get 'Cous' from COmanage")
            print("[ERROR] " + str(response))
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
            print("[ERROR] unable to get 'CoPeople' from COmanage")
            print("[ERROR] " + str(response))
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
                    print("[ERROR] unable to get 'Names' from COmanage")
                    print("[ERROR] " + str(response))
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
                    print("[ERROR] unable to get 'EmailAddresses' from COmanage")
                    print("[ERROR] " + str(response))
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
        # pprint(role)
        try:
            role_id = role['Id']
            # get comanage_cous id and name
            sql = """
            SELECT id, name from comanage_cous WHERE cou_id = '{0}'
            """.format(role['CouId'])
            dfq = dict_from_query(sql)
            co_cou_id = dfq[0].get('id')
            co_role_name = dfq[0].get('name')
            command = """
            INSERT INTO fabric_roles(cou_id, people_id, role_name, role_id)
            VALUES ({0}, {1}, '{2}', {3})
            ON CONFLICT ON CONSTRAINT fabric_role_duplicate
            DO NOTHING;
            """.format(int(co_cou_id), int(people_id), co_role_name, int(role_id))
            sql_list.append(command)
        except KeyError:
            pass
    commands = tuple(i for i in sql_list)
    print("[INFO] attempt to load roles:")
    run_sql_commands(commands)


def update_projects_data():
    cous = []
    sql = """
    SELECT name, description, created_date from comanage_cous;
    """
    dfq = dict_from_query(sql)
    for cou in dfq:
        cous.append({'name': cou.get('name'), 'desc': cou.get('description'), 'created_date': cou.get('created_date')})
    # update fabric_projects table
    sql_list = []
    temp_list = []
    for cou in cous:
        match = re.search("([0-9|a-f]{8}-(?:[0-9|a-f]{4}-){3}[0-9|a-f]{12})", cou.get('name'))
        if match and cou.get('name')[-3:] == '-pc':
            temp_list.append({'name': match[0], 'desc': cou.get('desc'), 'created_date': cou.get('created_date')})
    pprint(temp_list)
    cou_set = temp_list.copy()
    for cou in cou_set:
        print("#########")
        print(cou)
        sql = """
        SELECT fabric_people.uuid
        FROM fabric_people INNER JOIN fabric_roles
        ON fabric_people.id = fabric_roles.people_id
        WHERE fabric_roles.role_name = '{0}'
        """.format(cou.get('name') + '-pc')
        try:
            dfq = dict_from_query(sql)
            print(dfq)
            created_by = dfq[0].get('uuid')
        except KeyError or IndexError as err:
            print(err)
            created_by = DEFAULT_CREATED_BY
        print(created_by)
        command = """
        INSERT INTO fabric_projects(uuid, name, description, facility, created_by, created_time)
        VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}')
        ON CONFLICT ON CONSTRAINT projects_uuid
        DO NOTHING;
        """.format(cou.get('name'), cou.get('desc'), DEFAULT_DESCRIPTION, DEFAULT_FACILITY, created_by,
                   cou.get('created_date'))
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
    response = requests.get(
        url="https://127.0.0.1:8443/people",
        verify=False,
        cookies={
            'fabric-service': 'H4sIAAAAAAAA_3yVXZOruBGGf1G2-Bic4fLYBgzHkgehD9AdQhwDkkAz9tjAr0_h7J5KVTa5bJru93m7VdXtknUiafpLn6VkTV3Yp7d0REFzSHepsiU9ZOEf7ZK5jUcXYeI7L9JdOkKHs_jGS_1DsmA4G6pkkd5SBd3GRw9B4K1i-t4s6W4TkCzfBIaazQ_uhd-XPhxEorUY0a-a5Q-4wr4ayBOs1-XCuLlg3vGjci5J5QCWzvzYaWCipcKkPx8yLVhsxeH_cBjeCaZvLQ2_K-bqdJh64iNdsVm3r7y00tDv0gs6wcjGBmsGp4rRW9o_-7qE61ZTn5DTnMDuvIS_2c8mXPiy9fib2vgvHrVxrpKlW36SJ_S89O-PytM34cmH6INHY5rHNlNp6JIX4Wu-zfK-wGM6X47RVu8I766FDi3fvJrOkaf9-nd9hBe7MrkuZ08rmoRfnL094LBXFctMhdUMjuAJDe-giXyQVCsYrgE0cIBD5MLh-gC4msGaz3AFy-UIHFBk4fmQ5TmDAy_h-mfP316adXqcPWhFEo7Ce_sWfjaevbCTJZpAH3aVB3XjQ_Li798dyOIeJPkCsVbgWC3g-GPmCZjBcHUgTn3oEQ-w3IHF-wyHaIXHyAdr-gYH8rbtg0S_fW0MuiXTk9NuX5PQFurOAI0tjuDPxsQlYfqjJjrAChW5435iHBe1tkfM7ISUuyNlB1HSxZiifRtnFCl0aZWzYHaHIM5wUcJMEL6yUWdQ6VuhEaw1WQr29jwbGhRm7qnDn5WCW_4bD_uaOnxlurvlDJWQWSAo_-IxzBpH3_lprwTlLjumbp1kJX3x2UtF5UW4uqQjzOpSWmbcRCZx2R5pBQY6VVrSlz-NFHL5VCnJINFWeroXhDtMv_S_QLnnwHQT09LnLlmJmTn1uxun_9YXJzu0RHkFcyeQoDQf7UeNO4_h7NZ46cJPvK8x9SrPHWoyH4vRKupoiz39U3goJaP8n_9LAxY66s1fQCgIAHvFQ4u7bf5ZG4URYhrkjp14LNHLj7Ed9TuPDWkgSWgvzPbIm2-VCQq-7a_kl1YFljFLpePuuK8_qGvv2EV1HduoXvcfyFVPTGXWbnEyQ0FowCiiL_5h34MR3SrzDJrYHgvMM8GuTx51h1aF9nLiHJh5rYZMSZNZWPJBMOhVQ5YAhk7c1wCY-YuqJmi0LeGJX2qVfTEqfwqqSe13EEWuj41b11FwRxhC5OodZnaEJLhjYy-1IjM2dpTKJazsYKvjNzxa2JIwwngPiaPXgrkvvTrhCnnzX_v8RDiDNHKemKKhVe5n5b3md-Pk9d7_Mz-2xP3kPswEmycebfX_pZeCQ3AQjlvCIY7amHdFnB2IY6fKWIao7XI1j_i4t7UTMEEzB5vuwGgaMBrmTGXflda6jVAvkkzVCh7OFD046_pWT6507heRyAzr-CsnliNKWYX3T-Qgcy7jXxXTEyThDpKnV8f7iJ64Lt3cqVzrSk0flzIKOAU-cGGEVz0wzL-EambgSSbLmCAf3HMnxMKZnFrHe3oiM07iiZaZ5vrqc7fryUh3MOl8qfRnm9gFajpiHHm43BNUZnmNsw9E43Pl_vDBihYSdSMYry5m2akdERDH_ZkO_GeNtYsHPjYJmbEKPeFmfaXDIyuhbiK7KwxnOXnesaM7wfIAEnqmJqzpSVKmwl_1ECPC5opEgRHHOGqPMpFJFrUHxy9iu9Rkxk2SOtTEFWPB1JZ2BWUVUPfHLCM6Vc71Xg-oRITfC52dkOYEKx0DCj2Gm7nRr5vw5y1NZzA03-Dw9jwPr--6Pf3oL0PkAQwcsEY-GK631Oh1u8Gp5g_J4JSOzh9fn47zLv_5ket_fMvdW9b-4ggT805BPr7TW5IMPfisb2HrP_8VAAD__3Z-cUscCAAA'
        }
    )
    print(response)
    update_projects_data()
