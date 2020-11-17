from configparser import ConfigParser

import requests

config = ConfigParser()
config.read('swagger_server/config/config.ini')

COOKIE_NAME = config['uis']['cookie_name']
COOKIE_DOMAIN = config['uis']['cookie_domain']
UIS_API_URL = config['uis']['api_url']
UIS_API_PORT = config['uis']['api_port']
SSL_VERIFY = config.getboolean('uis', 'ssl_verify')


def uis_get_uuid_from_oidc_claim_sub(oidc_claim_sub, cookies):
    # check if user is the default-user
    if oidc_claim_sub == config['default-user']['oidc_claim_sub']:
        return config['default-user']['uuid']
    # otherwise call uis to get uuid from oidc_claim_sub
    params = {'oidc_claim_sub': str(oidc_claim_sub)}
    response = requests.get(
        url=UIS_API_URL + ':' + UIS_API_PORT + '/uuid/oidc_claim_sub',
        params=params,
        cookies=cookies,
        verify=SSL_VERIFY
    )
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        return ''
