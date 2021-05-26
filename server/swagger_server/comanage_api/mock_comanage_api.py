from configparser import ConfigParser
from time import strftime, gmtime

from . import CO_API_COID, CO_API_USERNAME, EMPTY_PARENT_FLAG, MOCK_ROLE_ID_FLAG
from ..response_code.utils import dict_from_query

config = ConfigParser()
config.read('swagger_server/config/config.ini')


def mock_comanage_add_new_cou(cou_name, cou_description):
    ## Example COU comanage-api search response
    # {
    #     'ResponseType': 'Cous',
    #     'Version': '1.0',
    #     'Cous': [
    #         {
    #             'ActorIdentifier': 'co_22.project-registry-mvp',
    #             'CoId': '22',
    #             'Created': '2020-12-01 21:51:40',
    #             'Deleted': False,
    #             'Description': 'Example project for FABRIC',
    #             'Id': '187',
    #             'Lft': '134',
    #             'Modified': '2020-12-01 21:51:40',
    #             'Name': '8f176062-958d-4cf6-bba2-74f40039b4f3-pm',
    #             'ParentId': '155',
    #             'Revision': '0',
    #             'Rght': '135',
    #             'Version': '1.0'
    #         }
    #     ]
    # }
    # get project id
    sql = """
    SELECT MAX(cou_id) AS max_cou_id FROM comanage_cous;
    """
    dfq = dict_from_query(sql)
    cou_id = int(dfq[0].get('max_cou_id')) + 1
    co_id = CO_API_COID
    # get project id
    sql = """
    SELECT MAX(rght) AS max_rght FROM comanage_cous;
    """
    dfq = dict_from_query(sql)
    cou_lft = int(dfq[0].get('max_rght')) + 1
    cou_rght = int(cou_lft) + 1
    mock_cou_data = {
        'ResponseType': 'Cous',
        'Version': '1.0',
        'Cous': [
            {
                'ActorIdentifier': str(CO_API_USERNAME),
                'CoId': str(CO_API_COID),
                'Created': str(strftime('%Y-%m-%d %H:%M:%S', gmtime())),
                'Deleted': False,
                'Description': str(cou_description),
                'Id': str(cou_id),
                'Lft': str(cou_lft),
                'Modified': str(strftime('%Y-%m-%d %H:%M:%S', gmtime())),
                'Name': str(cou_name),
                'ParentId': str(EMPTY_PARENT_FLAG),
                'Revision': '0',
                'Rght': str(cou_rght),
                'Version': '1.0'
            }
        ]
    }

    return mock_cou_data


def mock_comanage_remove_cou(cou_id):
    print('[INFO] mock remove co_cou data: CouId = {0}'.format(cou_id))
    return True


def mock_comanange_add_users_to_cou(co_person_id, co_cou_id):
    print('[INFO] mock add users to cou: co_person_id = {0}, co_cou_id = {1}'.format(co_person_id, co_cou_id))
    new_co_person_role = {
        'ResponseType': 'NewObject',
        'Version': '1.0',
        'ObjectType': 'CoPersonRole',
        'Id': MOCK_ROLE_ID_FLAG
    }

    return new_co_person_role, 'Active'


def mock_comanage_remove_users_from_cou(role_id):
    print('[INFO] mock removal of co_role_id: Id = {0}'.format(role_id))
    return True
