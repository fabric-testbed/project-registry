from configparser import ConfigParser

config = ConfigParser()
config.read('swagger_server/config/config.ini')

# COmanage API settings
CO_API_USERNAME = config.get('comanage-api', 'api_username')
CO_API_PASSWORD = config.get('comanage-api', 'api_key')
CO_API_COID = config.get('comanage-api', 'api_coid')
PARENT_COU_ID = config.get('comanage-api', 'projects_cou_id')
EMPTY_PARENT_FLAG = config.get('comanage-api', 'empty_parent_flag')

DEFAULT_USER_OIDC_CLAIM_SUB = config.get('default-user', 'oidc_claim_sub')
MOCK_ROLE_ID_FLAG = config.get('mock', 'mock_role_id_flag')
