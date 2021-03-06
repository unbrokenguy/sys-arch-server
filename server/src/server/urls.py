from django.urls import path, include
from server import settings
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

urlpatterns = [
    path("api/", include("rest_api.urls")),
]

docs_schema_view = get_schema_view(
    openapi.Info(
        title="Projects API",
        default_version="v1",
    ),
    url="http://127.0.0.1:8000/docs/swagger/",
    public=True,
    permission_classes=(AllowAny,),
)

if settings.DEBUG:
    docs_urls = [
        path("swagger/", docs_schema_view.with_ui("swagger"), name="schema-swagger-ui"),
    ]
    urlpatterns += [path("docs/", include(docs_urls))]
