from configparser import ConfigParser

config = ConfigParser()
config.read('swagger_server/config/config.ini')

# set mock levels
MOCK_DATA = config['mock']['data']
MOCK_COMANAGE_API = config['mock']['comanage_api']
MOCK_UIS_API = config['mock']['uis_api']

# set authorization level COUs
FABRIC_ACTIVE_USERS = config['fabric-cou']['fabric_active_users']
FACILITY_OPERATORS = config['fabric-cou']['facility_operators']
PROJECT_LEADS = config['fabric-cou']['project_leads']

# set default user uuid flag
DEFAULT_USER_UUID = config['default-user']['uuid']
