import os

from swagger_server.response_code.response_utils import CoreApiOptions

# Projects Options
PROJECTS_TAGS = CoreApiOptions('projects_tags_base.json')
if os.getenv('CORE_API_DEPLOYMENT_TIER') == 'production':
    PROJECTS_TAGS = PROJECTS_TAGS + CoreApiOptions('projects_tags_production.json')
elif os.getenv('CORE_API_DEPLOYMENT_TIER') == 'beta':
    PROJECTS_TAGS = PROJECTS_TAGS + CoreApiOptions('projects_tags_beta.json')
else:
    PROJECTS_TAGS = PROJECTS_TAGS + CoreApiOptions('projects_tags_alpha.json')
