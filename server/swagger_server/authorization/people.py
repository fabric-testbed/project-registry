from . import FACILITY_OPERATORS
from .api_util import get_api_person


def authorize_people_get(headers):
    # TODO: check if any authorization is required here at all
    # get api_user
    # api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))
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


def authorize_people_uuid_get(headers, uuid):
    # get api_user
    api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))

    # self - user is allowed to see details about themself
    if uuid == api_person.uuid:
        print('[INFO] self')
        return True
    # facility operators - allowed to perform all actions within project-registry
    if FACILITY_OPERATORS in api_person.roles:
        print('[INFO] ' + FACILITY_OPERATORS)
        return True

    # all others - not allowed to add project owners
    return False


def filter_people_uuid_get(headers, response):
    # get api_user
    api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))
    return response
