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
    def __init__(self, people_id: str=None, cilogon_uid: str=None, name: str=None):  # noqa: E501
        """PeopleShort - a model defined in Swagger

        :param people_id: The people_id of this PeopleShort.  # noqa: E501
        :type people_id: str
        :param cilogon_uid: The cilogon_uid of this PeopleShort.  # noqa: E501
        :type cilogon_uid: str
        :param name: The name of this PeopleShort.  # noqa: E501
        :type name: str
        """
        self.swagger_types = {
            'people_id': str,
            'cilogon_uid': str,
            'name': str
        }

        self.attribute_map = {
            'people_id': 'people_id',
            'cilogon_uid': 'cilogon_uid',
            'name': 'name'
        }
        self._people_id = people_id
        self._cilogon_uid = cilogon_uid
        self._name = name

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
    def people_id(self) -> str:
        """Gets the people_id of this PeopleShort.


        :return: The people_id of this PeopleShort.
        :rtype: str
        """
        return self._people_id

    @people_id.setter
    def people_id(self, people_id: str):
        """Sets the people_id of this PeopleShort.


        :param people_id: The people_id of this PeopleShort.
        :type people_id: str
        """

        self._people_id = people_id

    @property
    def cilogon_uid(self) -> str:
        """Gets the cilogon_uid of this PeopleShort.


        :return: The cilogon_uid of this PeopleShort.
        :rtype: str
        """
        return self._cilogon_uid

    @cilogon_uid.setter
    def cilogon_uid(self, cilogon_uid: str):
        """Sets the cilogon_uid of this PeopleShort.


        :param cilogon_uid: The cilogon_uid of this PeopleShort.
        :type cilogon_uid: str
        """

        self._cilogon_uid = cilogon_uid

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
