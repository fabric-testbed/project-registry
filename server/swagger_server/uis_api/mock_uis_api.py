from uuid import uuid4

from . import DEFAULT_USER_OIDC_CLAIM_SUB, DEFAULT_USER_UUID


def mock_uis_get_uuid_from_oidc_claim_sub(oidc_claim_sub):
    # check if user is the default-user
    if oidc_claim_sub == DEFAULT_USER_OIDC_CLAIM_SUB:
        return DEFAULT_USER_UUID

    return str(uuid4())
