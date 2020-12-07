import psycopg2
from swagger_server import Session

from ..uis_api.uis_api import uis_get_uuid_from_oidc_claim_sub


def dict_from_query(query=None):
    session = Session()
    a = None
    try:
        resultproxy = session.execute(query)
        d, a = {}, []
        for rowproxy in resultproxy:
            # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
            for column, value in rowproxy.items():
                # build up the dictionary
                d = {**d, **{column: value}}
            a.append(d)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if session is not None:
            session.close()

    return a


def run_sql_commands(commands):
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


def resolve_empty_people_uuid():
    sql = """
    SELECT id, oidc_claim_sub FROM fabric_people
    WHERE uuid = '';
    """
    dfq = dict_from_query(sql)
    if dfq:
        sql_list = []
        for person in dfq:
            people_id = person.get('id')
            oidc_claim_sub = person.get('oidc_claim_sub')
            uuid = uis_get_uuid_from_oidc_claim_sub(oidc_claim_sub)

            sql = """
            UPDATE fabric_people
            SET uuid = '{0}'
            WHERE fabric_people.id = {1};
            """.format(uuid, people_id)
            sql_list.append(sql)

        commands = tuple(i for i in sql_list)
        print("[INFO] attempt to update people uuid data")
        run_sql_commands(commands)


def filter_out_preexisting_project_members(project_members, project_id):
    new_project_members = []
    sql = """
    SELECT fabric_people.uuid
    FROM fabric_people INNER JOIN project_members ON fabric_people.id = project_members.people_id
    WHERE project_members.projects_id = {0};
    """.format(project_id)
    dfq = dict_from_query(sql)
    try:
        existing_project_members = dfq[0].get('uuid')
    except IndexError or TypeError:
        existing_project_members = []

    for member in project_members:
        if member not in existing_project_members:
            new_project_members.append(member)
        else:
            print('[INFO] Exclude {0} from new_project_members - already in the group'.format(member))

    return new_project_members


def filter_out_preexisting_project_owners(project_owners, project_id):
    new_project_owners = []
    sql = """
        SELECT fabric_people.uuid
        FROM fabric_people INNER JOIN project_owners ON fabric_people.id = project_owners.people_id
        WHERE project_owners.projects_id = {0};
        """.format(project_id)
    dfq = dict_from_query(sql)
    try:
        existing_project_owners = dfq[0].get('uuid')
    except IndexError or TypeError:
        existing_project_owners = []

    for member in project_owners:
        if member not in existing_project_owners:
            new_project_owners.append(member)
        else:
            print('[INFO] Exclude {0} from new_project_owners - already in the group'.format(member))

    return new_project_owners


def filter_out_nonexisting_project_members(project_members, project_id):
    remove_project_members = []
    sql = """
    SELECT fabric_people.uuid
    FROM fabric_people INNER JOIN project_members ON fabric_people.id = project_members.people_id
    WHERE project_members.projects_id = {0};
    """.format(project_id)
    dfq = dict_from_query(sql)
    existing_project_members = []
    try:
        for project_member in dfq:
            existing_project_members.append(project_member.get('uuid'))
    except IndexError or TypeError as error:
        print(error)

    for member in project_members:
        if member in existing_project_members:
            remove_project_members.append(member)
        else:
            print('[INFO] Exclude {0} from remove_project_members - not found in the group'.format(member))

    return remove_project_members


def filter_out_nonexisting_project_owners(project_owners, project_id):
    remove_project_owners = []
    sql = """
    SELECT fabric_people.uuid
    FROM fabric_people INNER JOIN project_owners ON fabric_people.id = project_owners.people_id
    WHERE project_owners.projects_id = {0};
    """.format(project_id)
    dfq = dict_from_query(sql)
    existing_project_owners = []
    try:
        for project_owner in dfq:
            existing_project_owners.append(project_owner.get('uuid'))
    except IndexError or TypeError as error:
        print(error)

    for member in project_owners:
        if member in existing_project_owners:
            remove_project_owners.append(member)
        else:
            print('[INFO] Exclude {0} from remove_project_owners - not found in the group'.format(member))

    return remove_project_owners
