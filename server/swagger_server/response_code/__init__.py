from configparser import ConfigParser

config = ConfigParser()
config.read('server/swagger_server/config/config.ini')

# set default user uuid flag
DEFAULT_USER_UUID = config.get('default-user', 'uuid')
DEFAULT_USER_NAME = config.get('default-user', 'name')
DEFAULT_USER_EMAIL = config.get('default-user', 'email')

# uis api information
COOKIE_NAME = config.get('uis', 'cookie_name')
COOKIE_DOMAIN = config.get('uis', 'cookie_domain')
UIS_API_URL = config.get('uis', 'api_url')
UIS_API_PORT = config.get('uis', 'api_port')
