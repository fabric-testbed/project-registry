from swagger_server.db_models import ApiVersion
from swagger_server.models.version import Version  # noqa: E501


def version_get():  # noqa: E501
    """version

    version # noqa: E501


    :rtype: Version
    """
    # response as Version()
    response = Version()
    ver = ApiVersion.query.limit(1).one_or_none()
    if ver:
        d_ver = ver.__asdict__()
        response.version = d_ver.get('version')
        response.gitsha1 = d_ver.get('gitsha1')

    return response
