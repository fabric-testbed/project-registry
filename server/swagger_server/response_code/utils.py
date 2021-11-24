# import psycopg2
import flask
# from swagger_server import Session
#
# from ..uis_api.uis_api import uis_get_uuid_from_oidc_claim_sub


# def dict_from_query(query=None):
#     session = Session()
#     a = None
#     try:
#         resultproxy = session.execute(query)
#         d, a = {}, []
#         for rowproxy in resultproxy:
#             # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
#             for column, value in rowproxy.items():
#                 # build up the dictionary
#                 d = {**d, **{column: value}}
#             a.append(d)
#     except (Exception, psycopg2.DatabaseError) as error:
#         print(error)
#     finally:
#         if session is not None:
#             session.close()
#
#     return a
#
#
# def run_sql_commands(commands):
#     session = Session()
#     try:
#         if isinstance(commands, tuple):
#             for command in commands:
#                 session.execute(command)
#         else:
#             session.execute(commands)
#         session.commit()
#         print("[INFO] data loaded successfully!")
#     except (Exception, psycopg2.DatabaseError) as error:
#         print(error)
#     finally:
#         if session is not None:
#             session.close()
#
#
# def validate_project_reference(project_uuid):
#     sql = """
#     SELECT id, name, created_by FROM fabric_projects WHERE uuid = '{0}';
#     """.format(project_uuid)
#     dfq = dict_from_query(sql)
#     if dfq:
#         try:
#             project_id = dfq[0].get('id')
#             project_name = dfq[0].get('name')
#             created_by = dfq[0].get('created_by')
#             return project_id, project_name, created_by
#         except IndexError or KeyError or TypeError as err:
#             print(err)
#             return -1, -1, -1
#     else:
#         return -1, -1, -1
#
#
# def validate_person_reference(person_list):
#     person_list_new = list(set(person_list))
#     person_list_unknown = []
#     for member_uuid in person_list_new:
#         sql = """
#         SELECT EXISTS (
#             SELECT 1 FROM fabric_people WHERE fabric_people.uuid = '{0}'
#         );
#         """.format(member_uuid)
#         dfq = dict_from_query(sql)
#         if not dfq[0].get('exists'):
#             person_list_unknown.append(member_uuid)
#
#     return person_list_new, person_list_unknown
#
#
# def validate_project_members_list(project_members, project_id):
#     project_members_new = filter_out_preexisting_project_members(list(set(project_members)), project_id)
#     project_members_unknown = []
#     for member_uuid in project_members_new:
#         sql = """
#         SELECT EXISTS (
#             SELECT 1 FROM fabric_people WHERE fabric_people.uuid = '{0}'
#         );
#         """.format(member_uuid)
#         dfq = dict_from_query(sql)
#         if not dfq[0].get('exists'):
#             project_members_unknown.append(member_uuid)
#
#     return project_members_new, project_members_unknown
#
#
# def validate_project_owners_list(project_owners, project_id):
#     project_owners_new = filter_out_preexisting_project_owners(list(set(project_owners)), project_id)
#     project_owners_unknown = []
#     for member_uuid in project_owners_new:
#         sql = """
#         SELECT EXISTS (
#             SELECT 1 FROM fabric_people WHERE fabric_people.uuid = '{0}'
#         );
#         """.format(member_uuid)
#         dfq = dict_from_query(sql)
#         if not dfq[0].get('exists'):
#             project_owners_unknown.append(member_uuid)
#
#     return project_owners_new, project_owners_unknown
#
#
# def resolve_empty_people_uuid():
#     sql = """
#     SELECT id, oidc_claim_sub FROM fabric_people
#     WHERE uuid = '';
#     """
#     dfq = dict_from_query(sql)
#     if dfq:
#         sql_list = []
#         for person in dfq:
#             people_id = person.get('id')
#             oidc_claim_sub = person.get('oidc_claim_sub')
#             uuid = uis_get_uuid_from_oidc_claim_sub(oidc_claim_sub)
#             if uuid:
#                 sql = """
#                 UPDATE fabric_people
#                 SET uuid = '{0}'
#                 WHERE fabric_people.id = {1};
#                 """.format(uuid, people_id)
#                 sql_list.append(sql)
#
#         commands = tuple(i for i in sql_list)
#         if commands:
#             print("[INFO] attempt to update people uuid data")
#             run_sql_commands(commands)
#
#
# def filter_out_preexisting_project_members(project_members, project_id):
#     new_project_members = []
#     sql = """
#     SELECT fabric_people.uuid
#     FROM fabric_people INNER JOIN project_members ON fabric_people.id = project_members.people_id
#     WHERE project_members.projects_id = {0};
#     """.format(project_id)
#     dfq = dict_from_query(sql)
#     try:
#         existing_project_members = dfq[0].get('uuid')
#     except IndexError or TypeError:
#         existing_project_members = []
#
#     for member in project_members:
#         if member not in existing_project_members:
#             new_project_members.append(member)
#         else:
#             print('[INFO] Exclude {0} from new_project_members - already in the group'.format(member))
#
#     return new_project_members
#
#
# def filter_out_preexisting_project_owners(project_owners, project_id):
#     new_project_owners = []
#     sql = """
#         SELECT fabric_people.uuid
#         FROM fabric_people INNER JOIN project_owners ON fabric_people.id = project_owners.people_id
#         WHERE project_owners.projects_id = {0};
#         """.format(project_id)
#     dfq = dict_from_query(sql)
#     try:
#         existing_project_owners = dfq[0].get('uuid')
#     except IndexError or TypeError:
#         existing_project_owners = []
#
#     for member in project_owners:
#         if member not in existing_project_owners:
#             new_project_owners.append(member)
#         else:
#             print('[INFO] Exclude {0} from new_project_owners - already in the group'.format(member))
#
#     return new_project_owners
#
#
# def filter_out_nonexisting_project_members(project_members, project_id):
#     remove_project_members = []
#     sql = """
#     SELECT fabric_people.uuid
#     FROM fabric_people INNER JOIN project_members ON fabric_people.id = project_members.people_id
#     WHERE project_members.projects_id = {0};
#     """.format(project_id)
#     dfq = dict_from_query(sql)
#     existing_project_members = []
#     try:
#         for project_member in dfq:
#             existing_project_members.append(project_member.get('uuid'))
#     except IndexError or TypeError as error:
#         print(error)
#
#     for member in project_members:
#         if member in existing_project_members:
#             remove_project_members.append(member)
#         else:
#             print('[INFO] Exclude {0} from remove_project_members - not found in the group'.format(member))
#
#     return remove_project_members
#
#
# def filter_out_nonexisting_project_owners(project_owners, project_id):
#     remove_project_owners = []
#     sql = """
#     SELECT fabric_people.uuid
#     FROM fabric_people INNER JOIN project_owners ON fabric_people.id = project_owners.people_id
#     WHERE project_owners.projects_id = {0};
#     """.format(project_id)
#     dfq = dict_from_query(sql)
#     existing_project_owners = []
#     try:
#         for project_owner in dfq:
#             existing_project_owners.append(project_owner.get('uuid'))
#     except IndexError or TypeError as error:
#         print(error)
#
#     for member in project_owners:
#         if member in existing_project_owners:
#             remove_project_owners.append(member)
#         else:
#             print('[INFO] Exclude {0} from remove_project_owners - not found in the group'.format(member))
#
#     return remove_project_owners


# TODO: refactor - find new location for this funciton
def cors_response(request, status_code=200, body=None, x_error=None):
    response = flask.Response()
    response.status_code = status_code
    response.data = body
    response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'DNT, User-Agent, X-Requested-With, If-Modified-Since, Cache-Control, Content-Type, Range'
    response.headers['Access-Control-Expose-Headers'] = 'Content-Length, Content-Range, X-Error'

    if x_error:
        response.headers['X-Error'] = x_error

    print(response)
    return response
