import connexion
import six

from swagger_server.models.people_long import PeopleLong  # noqa: E501
from swagger_server.models.people_short import PeopleShort  # noqa: E501
from swagger_server import util
from swagger_server.response_code import people_controller as rc


def people_get(person_name=None):  # noqa: E501
    """list of people

    List of people # noqa: E501

    :param person_name: Search People by Name (ILIKE)
    :type person_name: str

    :rtype: List[PeopleShort]
    """
    return rc.people_get(person_name)


def people_oidc_claim_sub_get(oidc_claim_sub):  # noqa: E501
    """person details by OIDC Claim sub

    Person details by OIDC Claim sub # noqa: E501

    :param oidc_claim_sub: Search People by OIDC Claim sub (exact match only)
    :type oidc_claim_sub: str

    :rtype: List[PeopleLong]
    """
    return rc.people_oidc_claim_sub_get(oidc_claim_sub)


def people_role_attribute_sync_get():  # noqa: E501
    """role attribute sync

    Synchronize COU Role Attributes # noqa: E501


    :rtype: None
    """
    return rc.people_role_attribute_sync_get()


def people_uuid_get(uuid):  # noqa: E501
    """person details by UUID

    Person details by UUID # noqa: E501

    :param uuid: People identifier as UUID
    :type uuid: str

    :rtype: PeopleLong
    """
    return rc.people_uuid_get(uuid)
