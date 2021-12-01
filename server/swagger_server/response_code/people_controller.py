import os

from flask import request

from swagger_server.db_models import FabricPeople
from swagger_server.models.people_long import PeopleLong  # noqa: E501
from swagger_server.models.people_short import PeopleShort  # noqa: E501
from .authorization_controller import cors_401, cors_response, get_api_user
from .local_controller import get_roles_per_person, get_projects_per_person, sync_roles_per_person


def people_get(person_name=None):  # noqa: E501
    """list of people

    List of people # noqa: E501

    :param person_name: Search People by Name (ILIKE)
    :type person_name: str

    :rtype: List[PeopleShort]
    """
    api_user = get_api_user(api_request=request)
    if not api_user.uuid:
        return cors_401()

    # ALLOW: fabric-active-users
    if not os.getenv('ROLE_ACTIVE_USERS') in api_user.roles:
        return cors_401()

    fab_people = []
    if person_name:
        people = FabricPeople.query.filter(
            (FabricPeople.name.ilike("%" + person_name + "%")) | (FabricPeople.email.ilike("%" + person_name + "%"))
        ).order_by(FabricPeople.name).all()
    else:
        people = FabricPeople.query.order_by(FabricPeople.name).all()
    for person in people:
        d_person = person.__asdict__()
        ps = PeopleShort()
        ps.name = d_person.get('name')
        ps.email = d_person.get('email')
        ps.uuid = d_person.get('uuid')
        fab_people.append(ps)
    response = fab_people

    return response


def people_oidc_claim_sub_get(oidc_claim_sub):  # noqa: E501
    """person details by OIDC Claim sub

    Person details by OIDC Claim sub # noqa: E501

    :param oidc_claim_sub: Search People by OIDC Claim sub (exact match only)
    :type oidc_claim_sub: str

    :rtype: List[PeopleLong]
    """
    api_user = get_api_user(api_request=request)
    if not api_user.uuid:
        return cors_401()

    # ALLOW: matching oidc_claim_sub or facility-operators
    if oidc_claim_sub != api_user.oidc_claim_sub and os.getenv('ROLE_FACILITY_OPERATORS') not in api_user.roles:
        return cors_401()

    pl = PeopleLong()
    person = FabricPeople.query.filter_by(oidc_claim_sub=oidc_claim_sub).one_or_none()
    if person:
        d_person = person.__asdict__()
        person_id = int(d_person.get('id'))
        pl.name = d_person.get('name')
        pl.email = d_person.get('email')
        pl.uuid = d_person.get('uuid')
        pl.oidc_claim_sub = d_person.get('oidc_claim_sub')
        pl.roles = get_roles_per_person(person_id=person_id)
        pl.projects = get_projects_per_person(person_id=person_id)
    else:
        return cors_response(
            request=request,
            status_code=404,
            body='OIDC Claim sub Not Found: {0}'.format(oidc_claim_sub),
            x_error='Not Found'
        )
    response = pl

    return response


def people_role_attribute_sync_get():  # noqa: E501
    """role attribute sync

    Synchronize COU Role Attributes # noqa: E501


    :rtype: None
    """
    api_user = get_api_user(api_request=request)
    if not api_user.uuid:
        return cors_401()

    if sync_roles_per_person(api_user.uuid):
        return 'OK'
    else:
        return cors_response(
            request=request,
            status_code=500,
            body='Unexpected error',
            x_error='Unexpected error'
        )


def people_uuid_get(uuid):  # noqa: E501
    """person details by UUID

    Person details by UUID # noqa: E501

    :param uuid: People identifier as UUID
    :type uuid: str

    :rtype: PeopleLong
    """
    api_user = get_api_user(api_request=request)
    if not api_user.uuid:
        return cors_401()

    # ALLOW: matching uuid or facility-operators
    if uuid != api_user.uuid and os.getenv('ROLE_FACILITY_OPERATORS') not in api_user.roles:
        return cors_401()

    pl = PeopleLong()
    person = FabricPeople.query.filter_by(uuid=uuid).one_or_none()
    if person:
        d_person = person.__asdict__()
        person_id = int(d_person.get('id'))
        pl.name = d_person.get('name')
        pl.email = d_person.get('email')
        pl.uuid = d_person.get('uuid')
        pl.oidc_claim_sub = d_person.get('oidc_claim_sub')
        pl.roles = get_roles_per_person(person_id=person_id)
        pl.projects = get_projects_per_person(person_id=person_id)
    else:
        return cors_response(
            request=request,
            status_code=404,
            body='UUID Not Found: {0}'.format(uuid),
            x_error='Not Found'
        )
    response = pl

    return response
