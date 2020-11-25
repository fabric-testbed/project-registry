from configparser import ConfigParser
from time import strftime, gmtime

from . import CO_API_COID, DEFAULT_USER_OIDC_CLAIM_SUB
from ..response_code.utils import dict_from_query

config = ConfigParser()
config.read('swagger_server/config/config.ini')


def mock_comanage_add_new_cou(cou_name, cou_description):
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
                'Version': '1.0',
                'Id': str(cou_id),
                'CoId': str(co_id),
                'Name': str(cou_name),
                'Description': str(cou_description),
                'Lft': str(cou_lft),
                'Rght': str(cou_rght),
                'Created': str(strftime('%Y-%m-%d %H:%M:%S', gmtime())),
                'Modified': str(strftime('%Y-%m-%d %H:%M:%S', gmtime())),
                'Revision': '1',
                'Deleted': 'False',
                'ActorIdentifier': str(DEFAULT_USER_OIDC_CLAIM_SUB)
            }
        ]
    }

    return mock_cou_data

## Example COU comanage-api search response
# {
#   'ResponseType': 'Cous',
#   'Version': '1.0',
#   'Cous': [
#     {
#       'Version': '1.0',
#       'Id': '178',
#       'CoId': '22',
#       'Name': 'bc3acf7e-2ab8-4900-b357-d188e0e9e9b6-po',
#       'Description': 'TEST PROJECT - project owners',
#       'ParentId': '155',
#       'Lft': '126',
#       'Rght': '127',
#       'Created': '2020-11-21 23:52:08',
#       'Modified': '2020-11-24 15:31:38',
#       'Revision': '1',
#       'Deleted': false,
#       'ActorIdentifier': 'http://cilogon.org/serverA/users/242181'
#     }
#   ]
# }
