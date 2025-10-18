from django.conf import settings
from django.http import HttpRequest


def constants(request: HttpRequest) -> dict[str, str]:
    return {
        "project_name": settings.PROJECT_NAME.capitalize(),
        "domain_name": settings.DOMAIN_NAME,
        "project_description": settings.PROJECT_DESCRIPTION,
        "contact_email": settings.EMAIL,
    }
