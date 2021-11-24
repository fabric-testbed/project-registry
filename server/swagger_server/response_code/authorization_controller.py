from flask import request, Response
from jwt import decode
import requests
import os
from json import JSONDecodeError
from swagger_server.db_models import FabricPeople
from swagger_server.models.people_long import PeopleLong
from .local_controller import get_roles_per_person, get_projects_per_person
from typing import Optional
from swagger_server.db import db


def cors_response(request, status_code=200, body=None, x_error=None):
    response = Response()
    response.status_code = status_code
    response.data = body
    response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'DNT, User-Agent, X-Requested-With, If-Modified-Since, Cache-Control, Content-Type, Range'
    response.headers['Access-Control-Expose-Headers'] = 'Content-Length, Content-Range, X-Error'

    if x_error:
        response.headers['X-Error'] = x_error

    return response


def cors_401():
    return cors_response(
        request=request,
        status_code=401,
        body='Unauthorized',
        x_error='Authentication required'
    )


def get_api_user(api_request: request) -> PeopleLong:
    api_person = PeopleLong()
    idp_idtoken = api_request.headers.get('X-Vouch-Idp-Idtoken', None)
    if not idp_idtoken:
        return api_person
    decoded_token = decode(idp_idtoken, options={"verify_signature": False})
    oidc_claim_sub = decoded_token.get('sub', None)
    if not oidc_claim_sub:
        return api_person
    fab_person = FabricPeople.query.filter_by(oidc_claim_sub=oidc_claim_sub).one_or_none()
    if fab_person:
        # check for uuid
        if fab_person.__asdict__().get('uuid', 'None') == 'None':
            print('[INFO] Checking with UIS for user UUID')
            uuid_found = get_user_uuid(api_request=api_request, oidc_claim_sub=oidc_claim_sub)
            if uuid_found:
                fab_person.uuid = uuid_found
                db.session.commit()
            else:
                return api_person
        fab_person = fab_person.__asdict__()
        person_id = int(fab_person.get('id'))
        api_person.name = fab_person.get('name')
        api_person.email = fab_person.get('email')
        api_person.uuid = fab_person.get('uuid')
        api_person.oidc_claim_sub = fab_person.get('oidc_claim_sub')
        api_person.roles = get_roles_per_person(person_id=person_id)
        api_person.projects = get_projects_per_person(person_id=person_id)
    else:
        return api_person

    return api_person


def get_user_uuid(api_request, oidc_claim_sub: str) -> Optional[str]:
    s = requests.Session()
    params = {'oidc_claim_sub': str(oidc_claim_sub)}
    auth_cookie = {
        os.getenv('UIS_AUTH_COOKIE_NAME'): api_request.cookies.get(os.getenv('UIS_AUTH_COOKIE_NAME'))
    }
    try:
        response = s.get(
            url=os.getenv('UIS_GET_USER_UUID_ENDPOINT'),
            params=params,
            cookies=auth_cookie,
            verify=False
        )
    except requests.exceptions.ConnectionError as e:
        print(e)
        return None
    finally:
        s.close()
    if response.status_code == requests.codes.ok:
        try:
            return response.json()
        except JSONDecodeError as e:
            print(e)
            return None
    else:
        return None
