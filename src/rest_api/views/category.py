from django.http import JsonResponse, HttpResponse
from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny
from rest_api.serializers import CategorySerializer
from rest_api.db import DataBase
from rest_api.views.authentication import is_authenticated


class CategoryViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    permission_classes = [AllowAny]
    serializer_class = CategorySerializer

    @is_authenticated
    def list(self, request, *args, **kwargs):
        """GET method (<api>/category/) that retrieve category list
        Returns:
            HttpResponse: Response with categories list in json
        """
        return JsonResponse([{"id": c[0], "name": c[1]} for c in DataBase.get_categories_list()], safe=False)

    @is_authenticated
    def retrieve(self, request, *args, **kwargs):
        """GET method (<api>/category/{pk}/) that retrieve file by category pk
        Returns:
            ReHttpResponse: response with file id and its category name in json if it was found or 404 with message.
        """
        file = DataBase.get_category_file(kwargs["pk"])
        if file:
            return JsonResponse([{"id": file.id, "name": file.category}], safe=False)
        else:
            return HttpResponse(
                '{"message": "Невозможно получить данные, категория не существует." }',
                status=404,
            )
