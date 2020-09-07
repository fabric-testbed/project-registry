import connexion
import six

from swagger_server.models.people_long import PeopleLong  # noqa: E501
from swagger_server.models.people_short import PeopleShort  # noqa: E501
from swagger_server import util
from swagger_server.response_code import people_controller as rc


def people_get():  # noqa: E501
    """list of people

    List of people # noqa: E501


    :rtype: List[PeopleShort]
    """
    return rc.people_get()


def people_uuid_get(uuid):  # noqa: E501
    """person details

    Person details # noqa: E501

    :param uuid: People identifier as UUID
    :type uuid: str

    :rtype: PeopleLong
    """
    return rc.people_uuid_get(uuid)
