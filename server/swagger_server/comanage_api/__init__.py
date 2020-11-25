from configparser import ConfigParser

config = ConfigParser()
config.read('swagger_server/config/config.ini')

CO_API_COID = config.get('comanage-api', 'api_coid')
EMPTY_PARENT_FLAG = config.get('comanage-api', 'empty_parent_flag')

DEFAULT_USER_OIDC_CLAIM_SUB = config.get('default-user', 'oidc_claim_sub')
