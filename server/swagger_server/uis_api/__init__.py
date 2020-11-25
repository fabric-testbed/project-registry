from configparser import ConfigParser

config = ConfigParser()
config.read('swagger_server/config/config.ini')

# set UIS api variables
COOKIE_DOMAIN = config.get('uis', 'cookie_domain')
COOKIE_NAME = config.get('uis', 'cookie_name')
UIS_API_URL = config.get('uis', 'api_url')
UIS_API_PORT = config.get('uis', 'api_port')

# default user variables
DEFAULT_USER_OIDC_CLAIM_SUB = config.get('default-user', 'oidc_claim_sub')
DEFAULT_USER_UUID = config.get('default-user', 'uuid')
