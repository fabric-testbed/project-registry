from configparser import ConfigParser

from .auth_utils import get_api_person
from ..uis_api.uis_api import uis_get_uuid_from_oidc_claim_sub
from ..response_code.utils import run_sql_commands

config = ConfigParser()
config.read('swagger_server/config/config.ini')

# set authorization level COUs
FACILITY_OPERATORS = config.get('fabric-cou', 'facility_operators')

# set default user uuid flag
DEFAULT_USER_UUID = config.get('default-user', 'uuid')


def authorize_people_get(headers):
    # TODO: check if any authorization is required here at all
    # allow mock data to pass
    if config.getboolean('mock', 'data'):
        return True
    # get api_user
    api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))
    if api_person.uuid == DEFAULT_USER_UUID:
        return False

    return True


def filter_people_get(headers, response):
    # get api_user
    api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))
    return response


def authorize_people_oidc_claim_sub_get(headers, oidc_claim_sub):
    # get api_user
    api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))

    # self - user is allowed to see details about themself
    if oidc_claim_sub == api_person.oidc_claim_sub:
        print('[INFO] self')
        return True
    # facility operators - allowed to perform all actions within project-registry
    if FACILITY_OPERATORS in api_person.roles:
        print('[INFO] ' + FACILITY_OPERATORS)
        return True

    # all others - not allowed to add project owners
    return False


def filter_people_oidc_claim_sub_get(headers, response):
    # get api_user
    api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))
    return response


def authorize_people_role_attribute_sync_get(headers):
    # TODO: check if any authorization is required here at all
    # allow mock data to pass
    if config.getboolean('mock', 'data'):
        return True, ''
    # get api_user
    api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))
    if api_person.uuid == DEFAULT_USER_UUID:
        return False, api_person

    return True, api_person


def filter_people_role_attribute_sync_get(headers, response):
    # get api_user
    api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))
    return response


def authorize_people_uuid_get(headers, uuid):
    # get api_user
    api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))

    # attempt to get uuid for user
    if not api_person.uuid:
        print("[INFO] UUID is empty for oidc_claim_sub = {0}".format(api_person.oidc_claim_sub))
        uuid = uis_get_uuid_from_oidc_claim_sub(api_person.oidc_claim_sub)
        if uuid:
            print("[INFO] UUID is found for oidc_claim_sub = {0}".format(api_person.oidc_claim_sub))
            command = """
            UPDATE fabric_people
            SET uuid = '{0}'
            WHERE fabric_people.oidc_claim_sub = '{1}';
            """.format(uuid, api_person.oidc_claim_sub)
            print("[INFO] attempt to update people uuid data for oidc_claim_sub = {0}".format(api_person.oidc_claim_sub))
            run_sql_commands(command)

    # self - user is allowed to see details about themself
    if uuid == api_person.uuid:
        print('[INFO] self')
        return True, str(api_person.uuid)
    # facility operators - allowed to perform all actions within project-registry
    if FACILITY_OPERATORS in api_person.roles:
        print('[INFO] ' + FACILITY_OPERATORS)
        return True, str(api_person.uuid)

    # all others - not allowed to add project owners
    return False, str(api_person.uuid)


def filter_people_uuid_get(headers, response):
    # get api_user
    api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))
    return response
