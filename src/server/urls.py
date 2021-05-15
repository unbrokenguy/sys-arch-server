"""All url paths
POST api/auth/sign_in/ - Redirect to authorization server
POST api/auth/sign_up/ - Redirect to authorization server
POST api/data/ - Create data (strings or files)
GET api/category/ - List of categories
GET api/data/{pk}/ - Retrieve data
GET api/category/{pk}/ - Retrieve category
"""
from django.contrib import admin
from django.urls import path, include
from rest_api.views import auth


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("rest_api.urls")),
    path("api/auth/<slug:method>/", auth),
]
