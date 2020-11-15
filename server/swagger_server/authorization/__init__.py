from configparser import ConfigParser

config = ConfigParser()
config.read('swagger_server/config/config.ini')

# set authorization level COUs
FABRIC_ACTIVE_USERS = config['fabric-cou']['fabric_active_users']
FACILITY_OPERATORS = config['fabric-cou']['facility_operators']
PROJECT_LEADS = config['fabric-cou']['project_leads']
