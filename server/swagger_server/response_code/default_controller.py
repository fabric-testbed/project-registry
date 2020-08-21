import connexion
import six

from flask import jsonify

from swagger_server.models.version import Version  # noqa: E501
from swagger_server import util


def version_get():  # noqa: E501
    """version

    version # noqa: E501


    :rtype: Version
    """
    response = Version()

    # mock version
    response.version = '1.0.0'
    response.gitsha1 = 'd943bb9fd09e00a2fc672df344a087e8dd89ffb0'

    return response
