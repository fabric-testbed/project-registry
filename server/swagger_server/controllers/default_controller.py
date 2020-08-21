import connexion
import six

from swagger_server.models.version import Version  # noqa: E501
from swagger_server import util
from swagger_server.response_code import default_controller as rc


def version_get():  # noqa: E501
    """version

    version # noqa: E501


    :rtype: Version
    """
    return rc.version_get()
