from configparser import ConfigParser
from pprint import pprint

from . import EMPTY_PARENT_FLAG, CO_API_COID
from .mock_comanage_api import mock_comanage_add_new_cou
from ..response_code.utils import run_sql_commands

config = ConfigParser()
config.read('swagger_server/config/config.ini')


def comanage_projects_add_members_put(project_uuid, project_members):
    project_cou_pm = str(project_uuid) + '-pm'
    if config.getboolean('mock', 'comanage_api'):
        return True

    return True


def comanage_projects_add_owners_put(project_uuid, project_owners):
    project_cou_po = str(project_uuid) + '-po'
    if config.getboolean('mock', 'comanage_api'):
        return True

    return True


def comanage_projects_create_post(project_uuid, project_name):
    project_cou_po = str(project_uuid) + '-po'
    project_cou_pm = str(project_uuid) + '-pm'
    cous_to_add = [project_cou_po, project_cou_pm]
    for cou_name in cous_to_add:
        cou = comanage_add_new_cou(cou_name, project_name)['Cous'][0]
        # pprint(cou)
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
        print("[INFO] attempt to load co_cou data: CoId = " + CO_API_COID)
        run_sql_commands(command)

    return True


def comanage_projects_remove_members_put(project_uuid, project_members):
    project_cou_pm = str(project_uuid) + '-pm'
    if config.getboolean('mock', 'comanage_api'):
        return True

    return True


def comanage_projects_remove_owners_put(project_uuid, project_owners):
    project_cou_po = str(project_uuid) + '-po'
    if config.getboolean('mock', 'comanage_api'):
        return True

    return True


def comanage_add_new_cou(cou_name, cou_description):
    cou_data = {'Cous': []}
    if config.getboolean('mock', 'comanage_api'):
        cou_data = mock_comanage_add_new_cou(cou_name, cou_description)
    # check for valid cou pattern
    # attempt to create cous
    # return status
    return cou_data


def comanage_remove_cou():
    # check for valid cou pattern
    # validate that cous are empty of users
    # attempt to remove cous
    # return status
    pass


def comanange_add_users_to_cou():
    # validate that cou exists
    # validate that users exist
    # attempt to add users to cou
    # return status
    pass


def comanage_remove_users_from_cou():
    # validate that cou exists
    # validate that users exist
    # attempt to remove users from cou
    # return status
    pass
