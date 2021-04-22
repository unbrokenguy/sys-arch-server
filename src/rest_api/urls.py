"""Rest Api urls
POST api/data/ - Create data (strings or files)
GET api/category/ - List of categories
GET api/data/{pk}/ - Retrieve data
GET api/category/{pk}/ - Retrieve category
"""
from rest_api.views import CategoryViewSet, DataViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r"data", DataViewSet, basename="api-data")
router.register(r"category", CategoryViewSet, basename="api-category")
urlpatterns = router.urls
