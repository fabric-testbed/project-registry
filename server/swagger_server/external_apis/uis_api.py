from configparser import ConfigParser

config = ConfigParser()
config.read('swagger_server/config/config.ini')

co_api_username = config['comanage-api']['api_key']
co_api_key = config['comanage-api']['api_key']


def uis_get_uuid_from_oidc_claim_sub(oidc_claim_sub):
    # TODO: get uuid from uis/uuid/oidc_claim_sub
    # check if user is the default-user
    if oidc_claim_sub == config['default-user']['oidc_claim_sub']:
        return config['default-user']['uuid']
    # otherwise call uis to get uuid from oidc_claim_sub
    print(oidc_claim_sub)
    return ''
