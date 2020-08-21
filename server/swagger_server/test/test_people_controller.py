# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.people_long import PeopleLong  # noqa: E501
from swagger_server.models.people_short import PeopleShort  # noqa: E501
from swagger_server.test import BaseTestCase


class TestPeopleController(BaseTestCase):
    """PeopleController integration test stubs"""

    def test_people_get(self):
        """Test case for people_get

        list of people
        """
        response = self.client.open(
            '//people',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_people_people_idget(self):
        """Test case for people_people_idget

        person details
        """
        response = self.client.open(
            '//people/{PEOPLE_ID}'.format(people_id='people_id_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
