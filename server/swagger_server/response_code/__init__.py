from configparser import ConfigParser

config = ConfigParser()
config.read('swagger_server/config/config.ini')

# set mock levels
MOCK_DATA = config['mock']['data']
MOCK_COMANAGE_API = config['mock']['comanage_api']
MOCK_UIS_API = config['mock']['uis_api']

# set default user uuid flag
DEFAULT_USER_UUID = config['default-user']['uuid']
DEFAULT_USER_NAME = config['default-user']['name']
DEFAULT_USER_EMAIL = config['default-user']['email']