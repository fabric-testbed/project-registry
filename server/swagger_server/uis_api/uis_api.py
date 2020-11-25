from configparser import ConfigParser

import requests
from flask import request

from . import UIS_API_URL, UIS_API_PORT, COOKIE_DOMAIN, COOKIE_NAME, \
    DEFAULT_USER_OIDC_CLAIM_SUB, DEFAULT_USER_UUID
from .mock_uis_api import mock_uis_get_uuid_from_oidc_claim_sub

config = ConfigParser()
config.read('swagger_server/config/config.ini')


def uis_get_uuid_from_oidc_claim_sub(oidc_claim_sub):
    # check for uis api mock
    if config.getboolean('mock', 'uis_api'):
        return mock_uis_get_uuid_from_oidc_claim_sub(oidc_claim_sub)
    # check if user is the default-user
    elif oidc_claim_sub == DEFAULT_USER_OIDC_CLAIM_SUB:
        return DEFAULT_USER_UUID
    # otherwise call uis to get uuid from oidc_claim_sub
    else:
        params = {'oidc_claim_sub': str(oidc_claim_sub)}
        s = requests.Session()
        cookie_value = request.cookies.get(COOKIE_NAME)
        cookie_obj = requests.cookies.create_cookie(
            domain=COOKIE_DOMAIN,
            name=COOKIE_NAME,
            value=cookie_value
        )
        s.cookies.set_cookie(cookie_obj)
        cookies = s.cookies

        response = requests.get(
            url=UIS_API_URL + ':' + UIS_API_PORT + '/uuid/oidc_claim_sub',
            params=params,
            cookies=cookies,
            verify=config.getboolean('uis', 'ssl_verify')
        )
        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            return ''
