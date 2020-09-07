#!/usr/bin/env python3
import re
import sys
from pprint import pprint
from uuid import uuid4

import psycopg2

sys.path.append("..")

from database import Session, LDAP_PARAMS
from ldap3 import Connection, Server, ALL

# Variables

# default values
DEFAULT_NAME = 'INSERT_PROJECT_NAME'
DEFAULT_DESCRIPTION = 'INSERT_PROJECT_DESCRIPTION'
DEFAULT_FACILITY = 'INSERT_PROJECT_FACILITY'

# Attributes to request from COmanage LDAP
ATTRIBUTES = [
    'cn',
    'eduPersonPrincipalName',
    'isMemberOf',
    'mail',
    'uid'
]

# mocks for testing
mock_cou = [
    'CO:COU:project-leads:members:active',
    'CO:COU:facility-operators:members:active',
    'CO:COU:deadbeef-dead-beef-dead-beefdeadbeef:members:active',
    'CO:COU:deadbeef-dead-beef-dead-beefdeadbeef-pl:members:active',
    'CO:COU:deadbeef-dead-beef-dead-beefdeadbeef-pm:members:active',
    'CO:COU:deadbeef-dead-beef-dead-beefdeadbeef-po:members:active'
]
mock_people = [
    {
        'cn': 'John Q. Public',
        'eduPersonPrincipalName': 'public@project-registry.org',
        'isMemberOf': [
            'CO:COU:deadbeef-dead-beef-dead-beefdeadbeef:members:active',
            'CO:COU:deadbeef-dead-beef-dead-beefdeadbeef-pl:members:active',
            'CO:COU:deadbeef-dead-beef-dead-beefdeadbeef-pm:members:active',
            'CO:COU:deadbeef-dead-beef-dead-beefdeadbeef-po:members:active',
            'CO:COU:facility-operators:members:active',
            'CO:COU:project-leads:members:active'
        ],
        'mail': 'public@project-registry.org',
        'uid': 'http://cilogon.org/serverA/users/000001'
    },
    {
        'cn': 'Eliza Fuller',
        'eduPersonPrincipalName': 'efuller@project-registry.org',
        'isMemberOf': [],
        'mail': 'efuller@not-project-registry.org',
        'uid': 'http://cilogon.org/serverT/users/12345678'
    },
    {
        'cn': 'Kendra Theory',
        'eduPersonPrincipalName': 'ktheory@project-registry.org',
        'isMemberOf': [
            'CO:COU:project-leads:members:active'
        ],
        'mail': 'ktheory@email.project-registry.org',
        'uid': 'http://cilogon.org/serverA/users/87654321'
    },
    {
        'cn': 'Yolanda Guerra',
        'eduPersonPrincipalName': 'yolanda@@project-registry.org',
        'isMemberOf': [
            'CO:COU:deadbeef-dead-beef-dead-beefdeadbeef:members:active',
            'CO:COU:deadbeef-dead-beef-dead-beefdeadbeef-pm:members:active',
            'CO:COU:deadbeef-dead-beef-dead-beefdeadbeef-po:members:active'
        ],
        'mail': 'yolandaguerra@not-project-registry.org',
        'uid': 'http://cilogon.org/serverT/users/24681357'
    }
]

# COmanage LDAP server connection
server = Server(LDAP_PARAMS['host'], use_ssl=True, get_info=ALL)


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


def get_people_list():
    print("[INFO] get COmanage people list")
    ldap_search_filter = '(objectclass=person)'
    conn = Connection(server, LDAP_PARAMS['user'], LDAP_PARAMS['password'], auto_bind=True)
    objects_found = conn.search(
        LDAP_PARAMS['search_base'],
        ldap_search_filter,
        attributes=ATTRIBUTES
    )
    people = []
    if objects_found:
        print("[INFO] people objects found")
        for entry in conn.entries:
            print("       -----------------")
            obj = {}
            for attr in ATTRIBUTES:
                if attr == 'isMemberOf':
                    print(str(attr) + ": " + str(entry[str(attr)]).strip("'"))
                    groups = []
                    for group in entry[attr]:
                        if re.search("(CO:COU:(?:\w+-{1})+\w+:members:active)", str(group)):
                            groups.append(str(group))
                    obj[str(attr)] = groups
                else:
                    print(str(attr) + ": " + str(entry[str(attr)]))
                    obj[str(attr)] = str(entry[str(attr)])
            people.append(obj)
    conn.unbind()
    print("[INFO] people objects returned")
    pprint(people)
    return people


def get_cou_list():
    print("[INFO] get COmanage cou list")
    ldap_search_filter = '(objectclass=groupOfNames)'
    conn = Connection(server, LDAP_PARAMS['user'], LDAP_PARAMS['password'], auto_bind=True)
    objects_found = conn.search(
        LDAP_PARAMS['search_base'],
        ldap_search_filter,
        attributes='cn'
    )
    cou = []
    if objects_found:
        print("[INFO] cou objects found")
        for entry in conn.entries:
            pprint(entry['cn'])
            for group in entry['cn']:
                if re.search("(CO:COU:(?:\w+-{1})+\w+:members:active)", str(group)):
                    cou.append(str(group))
    conn.unbind()
    print("[INFO] cou objects returned")
    pprint(cou)
    return cou


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


def load_project_data():
    if str(LDAP_PARAMS['mock']).lower() == 'true':
        cous = mock_cou
        print("[INFO] *** MOCK COU DATA ***")
        pprint(cous)
    else:
        cous = get_cou_list()

    sql_list = []
    temp_list = []
    for cou in cous:
        match = re.search("([0-9|a-f]{8}-(?:[0-9|a-f]{4}-){3}[0-9|a-f]{12})", cou)
        if match:
            temp_list.append(match[0])
    cou_list = set(temp_list)
    for cou in cou_list:
        command = """
        INSERT INTO fabric_projects(uuid, cou, name, description, facility)
        VALUES ('{0}', 'CO:COU:{0}:members:active', '{1}', '{2}', '{3}')
        ON CONFLICT ON CONSTRAINT projects_cou
        DO NOTHING
        """.format(cou, DEFAULT_NAME, DEFAULT_DESCRIPTION, DEFAULT_FACILITY)
        sql_list.append(command)
    commands = tuple(i for i in sql_list)
    print("[INFO] attempt to load project data")
    run_sql_commands(commands)


def load_relationship_data(people):
    session = Session()
    sql_list = []
    for person in people:
        # get people_id (pk) from fabric_people
        sql = """
        SELECT id from fabric_people WHERE cilogon_id = '{0}'
        """.format(person['uid'])
        dfq = dict_from_query(sql)
        people_id = dfq[0]['id']
        # if facility-operators - set is_facility_operator = True
        if "CO:COU:facility-operators:members:active" in person['isMemberOf']:
            is_facility_operator = True
        else:
            is_facility_operator = False
        # if project-leads - set is_project_lead = True
        if "CO:COU:project-leads:members:active" in person['isMemberOf']:
            is_project_lead = True
        else:
            is_project_lead = False
        sql = """
        UPDATE fabric_people
        SET is_facility_operator = '{0}',
            is_project_lead = '{1}'
        WHERE fabric_people.id = {2};
        """.format(bool(is_facility_operator), bool(is_project_lead), int(people_id))
        sql_list.append(sql)
        # if isMemberOf attribute contains data
        for cou in person['isMemberOf']:
            # add cou to roles table
            sql = """
            INSERT INTO roles(people_id, role)
            VALUES ('{0}', '{1}')
            ON CONFLICT ON CONSTRAINT roles_duplicate
            DO NOTHING
            """.format(int(people_id), cou)
            sql_list.append(sql)

            # if project - if is_facility_operator = True, set facility_operators (projects_id, people_id)
            is_project_cou = False
            if re.search("CO:COU:([0-9|a-f]{8}-(?:[0-9|a-f]{4}-){3}[0-9|a-f]{12}):members:active", cou):
                is_project_cou = True
            if is_project_cou and is_facility_operator:
                sql = """
                SELECT id from fabric_projects WHERE cou = '{0}'
                """.format(cou)
                dfq = dict_from_query(sql)
                project_id = dfq[0]['id']
                command = """
                INSERT INTO facility_operators(projects_id, people_id)
                VALUES ('{0}', '{1}')
                ON CONFLICT ON CONSTRAINT facility_operators_duplicate
                DO NOTHING
                """.format(int(project_id), int(people_id))
                sql_list.append(command)
            #   if project/project-leads - set project_leads (projects_id, people_id)
            if re.search("CO:COU:([0-9|a-f]{8}-(?:[0-9|a-f]{4}-){3}[0-9|a-f]{12})-pl:members:active", cou):
                project_cou = re.sub('-pl', '', cou)
                sql = """
                SELECT id from fabric_projects WHERE cou = '{0}'
                """.format(project_cou)
                dfq = dict_from_query(sql)
                project_id = dfq[0]['id']
                command = """
                INSERT INTO project_leads(projects_id, people_id)
                VALUES ('{0}', '{1}')
                ON CONFLICT ON CONSTRAINT project_leads_duplicate
                DO NOTHING
                """.format(int(project_id), int(people_id))
                sql_list.append(command)
            #   if project/project-owners - set project_owners (projects_id, people_id)
            if re.search("CO:COU:([0-9|a-f]{8}-(?:[0-9|a-f]{4}-){3}[0-9|a-f]{12})-po:members:active", cou):
                project_cou = re.sub('-po', '', cou)
                sql = """
                SELECT id from fabric_projects WHERE cou = '{0}'
                """.format(project_cou)
                dfq = dict_from_query(sql)
                project_id = dfq[0]['id']
                command = """
                INSERT INTO project_owners(projects_id, people_id)
                VALUES ('{0}', '{1}')
                ON CONFLICT ON CONSTRAINT project_owners_duplicate
                DO NOTHING
                """.format(int(project_id), int(people_id))
                sql_list.append(command)
            #   if project/project-members - set project_members (projects_id, people_id)
            if re.search("CO:COU:([0-9|a-f]{8}-(?:[0-9|a-f]{4}-){3}[0-9|a-f]{12})-pm:members:active", cou):
                project_cou = re.sub('-pm', '', cou)
                sql = """
                SELECT id from fabric_projects WHERE cou = '{0}'
                """.format(project_cou)
                dfq = dict_from_query(sql)
                project_id = dfq[0]['id']
                command = """
                INSERT INTO project_members(projects_id, people_id)
                VALUES ('{0}', '{1}')
                ON CONFLICT ON CONSTRAINT project_members_duplicate
                DO NOTHING
                """.format(int(project_id), int(people_id))
                sql_list.append(command)

    session.close()
    commands = tuple(i for i in sql_list)
    print("[INFO] attempt to load relationship data")
    run_sql_commands(commands)


def load_people_data():
    if str(LDAP_PARAMS['mock']).lower() == 'true':
        people = mock_people
        print("[INFO] *** MOCK PEOPLE DATA ***")
        pprint(people)
    else:
        people = get_people_list()

    sql_list = []
    for person in people:
        people_uuid = uuid4()
        command = """
        INSERT INTO fabric_people(uuid, cilogon_id, name, email, eppn, is_facility_operator, is_project_lead)
        VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', FALSE, FALSE)
        ON CONFLICT ON CONSTRAINT cilogon_uid
        DO NOTHING
        """.format(people_uuid, person['uid'], person['cn'], person['mail'], person['eduPersonPrincipalName'])
        sql_list.append(command)
    commands = tuple(i for i in sql_list)
    print("[INFO] attempt to load people data")
    run_sql_commands(commands)
    load_relationship_data(people)


if __name__ == '__main__':
    if str(LDAP_PARAMS['mock']).lower() == 'true':
        print("[INFO] *** USING MOCK DATA ***")
    load_version_data()
    load_project_data()
    load_people_data()
