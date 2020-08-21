import connexion
import six

from swagger_server.models.people_long import PeopleLong  # noqa: E501
from swagger_server.models.people_short import PeopleShort  # noqa: E501
from swagger_server import util


def people_get():  # noqa: E501
    """list of people

    list of people # noqa: E501


    :rtype: List[PeopleShort]
    """
    response = []
    people = PeopleShort()

    # mock response
    people.people_id = 'e6f42656-15db-4b4f-af90-00492ca603c1'
    people.cilogon_uid = 'http://cilogon.org/serverA/users/242181'
    people.name = 'Michael Stealey'
    response.append(people)

    return response


def people_people_idget(people_id):  # noqa: E501
    """person details

    person details # noqa: E501

    :param people_id: People identifier as UUID
    :type people_id: str

    :rtype: PeopleLong
    """
    response = PeopleLong()

    # mock response
    response.people_id = 'e6f42656-15db-4b4f-af90-00492ca603c1'
    response.cilogon_uid = 'http://cilogon.org/serverA/users/242181'
    response.name = 'Michael Stealey'
    response.roles = [
        'CO:COU:FABRIC-LEAD:members:active',
        'CO:COU:FABRIC-OWNER:members:active',
        'CO:COU:FABRIC-MEMBER:members:active'
    ]
    response.projects = [
        'ea806951-a22e-4e85-bc70-4ce74b1967b9'
    ]

    return response
