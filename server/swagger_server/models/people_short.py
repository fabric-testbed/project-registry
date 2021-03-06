# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class PeopleShort(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, uuid: str=None, name: str=None, email: str=None):  # noqa: E501
        """PeopleShort - a model defined in Swagger

        :param uuid: The uuid of this PeopleShort.  # noqa: E501
        :type uuid: str
        :param name: The name of this PeopleShort.  # noqa: E501
        :type name: str
        :param email: The email of this PeopleShort.  # noqa: E501
        :type email: str
        """
        self.swagger_types = {
            'uuid': str,
            'name': str,
            'email': str
        }

        self.attribute_map = {
            'uuid': 'uuid',
            'name': 'name',
            'email': 'email'
        }
        self._uuid = uuid
        self._name = name
        self._email = email

    @classmethod
    def from_dict(cls, dikt) -> 'PeopleShort':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The People_short of this PeopleShort.  # noqa: E501
        :rtype: PeopleShort
        """
        return util.deserialize_model(dikt, cls)

    @property
    def uuid(self) -> str:
        """Gets the uuid of this PeopleShort.


        :return: The uuid of this PeopleShort.
        :rtype: str
        """
        return self._uuid

    @uuid.setter
    def uuid(self, uuid: str):
        """Sets the uuid of this PeopleShort.


        :param uuid: The uuid of this PeopleShort.
        :type uuid: str
        """

        self._uuid = uuid

    @property
    def name(self) -> str:
        """Gets the name of this PeopleShort.


        :return: The name of this PeopleShort.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name of this PeopleShort.


        :param name: The name of this PeopleShort.
        :type name: str
        """

        self._name = name

    @property
    def email(self) -> str:
        """Gets the email of this PeopleShort.


        :return: The email of this PeopleShort.
        :rtype: str
        """
        return self._email

    @email.setter
    def email(self, email: str):
        """Sets the email of this PeopleShort.


        :param email: The email of this PeopleShort.
        :type email: str
        """

        self._email = email
