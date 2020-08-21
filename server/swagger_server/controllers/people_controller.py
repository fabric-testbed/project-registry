import connexion
import six

from swagger_server.models.people_long import PeopleLong  # noqa: E501
from swagger_server.models.people_short import PeopleShort  # noqa: E501
from swagger_server import util
from swagger_server.response_code import people_controller as rc


def people_get():  # noqa: E501
    """list of people

    list of people # noqa: E501


    :rtype: List[PeopleShort]
    """
    return rc.people_get()


def people_people_idget(people_id):  # noqa: E501
    """person details

    person details # noqa: E501

    :param people_id: People identifier as UUID
    :type people_id: str

    :rtype: PeopleLong
    """
    return rc.people_people_idget(people_id)
