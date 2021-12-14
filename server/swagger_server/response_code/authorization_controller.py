import os
from json import JSONDecodeError
from typing import Optional

import requests
from flask import request, Response
from jwt import decode

from comanage_api import ComanageApi

from swagger_server.db import db
from swagger_server.db_models import FabricPeople, FabricRoles, FabricCous
from swagger_server.models.people_long import PeopleLong
from .local_controller import get_roles_per_person, get_projects_per_person

api = ComanageApi(
    co_api_url=os.getenv('COMANAGE_API_URL'),
    co_api_user=os.getenv('COMANAGE_API_USER'),
    co_api_pass=os.getenv('COMANAGE_API_PASS'),
    co_api_org_id=os.getenv('COMANAGE_API_CO_ID'),
    co_api_org_name=os.getenv('COMANAGE_API_CO_NAME'),
    co_ssh_key_authenticator_id=os.getenv('COMANAGE_API_SSH_KEY_AUTHENTICATOR_ID')
)


def cors_response(request, status_code=200, body=None, x_error=None):
    response = Response()
    response.status_code = status_code
    response.data = body
    response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = \
        'DNT, User-Agent, X-Requested-With, If-Modified-Since, Cache-Control, Content-Type, Range'
    response.headers['Access-Control-Expose-Headers'] = 'Content-Length, Content-Range, X-Error'

    if x_error:
        response.headers['X-Error'] = x_error

    return response


def cors_401():
    return cors_response(
        request=request,
        status_code=401,
        body='Unauthorized',
        x_error='Authentication and/or Authorization required'
    )


def load_fabric_person(co_person_id: int):
    print("Load/Update database table 'fabric_people' as FabricPeople")
    co_people = api.copeople_view_one(coperson_id=co_person_id).get('CoPeople', [])
    for co_person in co_people:
        co_person_id = co_person.get('Id')
        fab_person = FabricPeople.query.filter_by(co_person_id=co_person_id).one_or_none()
        if fab_person:
            print("Update entry in 'fabric_people' table for CouId: {0}".format(co_person_id))
            found_person = True
        else:
            print("Create entry in 'fabric_people' table for CouId: {0}".format(co_person_id))
            found_person = False
            fab_person = FabricPeople()
            fab_person.co_id = co_person.get('CoId')
            fab_person.co_person_id = co_person_id
            fab_person.oidc_claim_sub = oidc_claim_sub_from_coperson_id(co_person_id)
        fab_person.email = official_email_from_coperson_id(co_person_id)
        fab_person.name = primary_name_from_coperson_id(co_person_id)
        fab_person.co_status = co_person.get('Status')
        if not found_person:
            print("--> name: {0} | email: {1} | oidc_claim_sub {2}".format(
                fab_person.name, fab_person.email, fab_person.oidc_claim_sub))
            db.session.add(fab_person)
        db.session.commit()
    db.session.commit()


def load_fabric_person_roles(co_person_id: int):
    print("Load/Update database table 'fabric_roles' as FabricRoles")
    co_person_ids = [co_person_id]
    for co_person_id in co_person_ids:
        person = FabricPeople.query.filter_by(co_person_id=co_person_id).one_or_none()
        co_roles = api.coperson_roles_view_per_coperson(coperson_id=co_person_id)
        if co_roles:
            co_roles = co_roles.get('CoPersonRoles', [])
            for co_role in co_roles:
                co_role_id = co_role.get('Id')
                co_cou_id = co_role.get('CouId')
                status = co_role.get('Status')
                if person and co_cou_id and status:
                    role = FabricRoles.query.filter_by(role_id=co_role_id).one_or_none()
                    if not role:
                        print("Create entry in 'roles' table for CoPersonRolesId: {0}".format(co_role_id))
                        role = FabricRoles()
                        role_cou = FabricCous.query.filter_by(cou_id=co_cou_id).one_or_none()
                        if role_cou:
                            role.cou_id = role_cou.__asdict__().get('id')
                            role.role_name = role_cou.__asdict__().get('name')
                        else:
                            print("CoPersonRolesId: {0} is missing 'CouId'".format(co_role_id))
                            continue
                        role.role_id = co_role_id
                        role.people_id = person.id
                        role.status = status
                        db.session.add(role)
                        db.session.commit()
                    else:
                        print("Update entry in 'roles' table for CoPersonRolesId: {0}".format(co_role_id))
                        role.status = status
                        db.session.commit()
                else:
                    print("CoPersonRolesId: {0} is missing 'CouId'".format(co_role_id))
    db.session.commit()


def primary_name_from_coperson_id(co_person_id: int) -> str:
    primary_name = ''
    co_names = api.names_view_per_person(person_type='copersonid', person_id=co_person_id).get('Names', [])
    for co_name in co_names:
        if co_name.get('PrimaryName', False):
            family = co_name.get('Family', '')
            middle = co_name.get('Middle', '')
            given = co_name.get('Given', '')
            if middle:
                primary_name = given + ' ' + middle + ' ' + family
            else:
                primary_name = given + ' ' + family

    return primary_name


def official_email_from_coperson_id(co_person_id: int) -> str:
    official_email = ''
    co_emails = api.email_addresses_view_per_person(
        person_type='copersonid',
        person_id=co_person_id
    ).get('EmailAddresses', [])
    for co_email in co_emails:
        if co_email.get('Type') == 'official':
            official_email = co_email.get('Mail')
            break

    return official_email


def oidc_claim_sub_from_coperson_id(co_person_id: int) -> str:
    oidc_claim_sub = ''
    co_identifiers = api.identifiers_view_per_entity(
        entity_type='copersonid',
        entity_id=co_person_id
    ).get('Identifiers', [])
    for ident in co_identifiers:
        if ident.get('Type', None) == 'oidcsub':
            oidc_claim_sub = ident.get('Identifier', '')
            break

    return oidc_claim_sub


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
        # check if oidc_sub is registered with UIS
        print('[INFO] Checking with UIS for user UUID')
        uuid_found = get_user_uuid(api_request=api_request, oidc_claim_sub=oidc_claim_sub)
        if uuid_found:
            # attempt to match co_person by attributes in id token
            idt_email = decoded_token.get('email', None)
            idt_given = decoded_token.get('given_name', None)
            idt_family = decoded_token.get('family_name', None)
            if idt_email:
                co_person = api.copeople_match(mail=idt_email).get('CoPeople', [])
            else:
                co_person = api.copeople_match(given=idt_given, family=idt_family).get('CoPeople', [])
            # get co_person_id and update local database
            co_person_id = co_person[0].get('Id')
            load_fabric_person(co_person_id=co_person_id)
            load_fabric_person_roles(co_person_id=co_person_id)
            # attempt to get api user again
            api_person = get_api_user(api_request=api_request)
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
