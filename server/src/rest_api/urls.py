from rest_api.views import UserInputViewSet, FileViewSet, CategoryViewSet, DataViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r"file", FileViewSet, basename="api-file")
router.register(r"user_input", UserInputViewSet, basename="api-user-input")
router.register(r"data", DataViewSet, basename="api-data")
router.register(r"category", CategoryViewSet, basename="api-category")
urlpatterns = router.urls
