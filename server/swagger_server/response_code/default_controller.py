from swagger_server.models.version import Version  # noqa: E501

from .utils import dict_from_query


def version_get():  # noqa: E501
    """version

    version # noqa: E501


    :rtype: Version
    """
    # response as Version()
    response = Version()

    sql = """
    SELECT * from version
    FETCH FIRST ROW ONLY;
    """

    # construct response object
    dfq = dict_from_query(sql)[0]
    print("[INFO] query database for version information")
    response.version = dfq['version']
    response.gitsha1 = dfq['gitsha1']

    return response
