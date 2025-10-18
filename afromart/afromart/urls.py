from collections.abc import Sequence

from django.conf import settings
from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path
from django.views.generic import RedirectView

TITLE = settings.PROJECT_NAME.capitalize()
admin.site.site_title = TITLE
admin.site.site_header = TITLE
admin.site.index_title = "#dashboard"


urlpatterns: Sequence[URLPattern | URLResolver] = [
    path(
        route="favicon.ico",
        view=RedirectView.as_view(
            url="/static/img/favicon/favicon.ico", permanent=True
        ),
    ),
    path(route="gate/", view=include("gate.urls", namespace="gate")),
    path(route="a/", view=admin.site.urls),
]
