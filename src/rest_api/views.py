import re
from django.http import JsonResponse, HttpResponse
from rest_framework import viewsets, mixins
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_api.serializers import UserInputSerializer, FileSerializer, CategorySerializer
from rest_api.models import File, Category
from rest_api.custom_orm import CustomOrm
from rest_api.utils import guess_file_category


class DataViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    def retrieve(self, request, *args, **kwargs):
        orm = CustomOrm()
        checking = orm.get_category_file(kwargs["pk"])
        resp = orm.get_data_by_id_and_delete(kwargs["pk"])
        data = resp[0]
        content_type = resp[1]
        if data:
            return HttpResponse(data, content_type=content_type)
        elif checking:
            return HttpResponse(
                data='{"message": "Невозможно получить запись, запись уже была получена." }',
                status=404,
            )
        return HttpResponse(
            data='{"message": "Невозможно получить запись, запись не сущесвует." }',
            status=404,
        )


class FileViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    parser_classes = (
        FormParser,
        MultiPartParser,
    )
    permission_classes = [AllowAny]
    queryset = File.objects.all()
    serializer_class = FileSerializer

    def create(self, request, *args, **kwargs):
        orm = CustomOrm()
        _name = request.FILES["data"].name
        _category, _content_type = guess_file_category(_name)
        _data = request.FILES["data"].read()
        data = orm.create_data(_data, _category, _content_type)
        if data:
            return JsonResponse({"id": data.id, "category": data.category})
        return HttpResponse(
            data='{"message": "Невозможно создать запись, запись такой категории уже существует." }',
            status=400,
        )


class UserInputViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    permission_classes = [AllowAny]
    serializer_class = UserInputSerializer

    def create(self, request, *args, **kwargs):
        orm = CustomOrm()
        _data = request.data["data"]
        _category = "Числа" if re.match(r"^[-+]?\d+([.,]\d+)?$", _data) else "Строки"
        data = orm.create_data(data=_data, category=_category, content_type="plain/text")
        if data:
            return JsonResponse({"id": data.id, "category": data.category})
        return HttpResponse(
            data='{"message": "Невозможно создать запись, запись такой категории уже существует." }',
            status=400,
        )


class CategoryViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    permission_classes = [AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def list(self, request, *args, **kwargs):
        orm = CustomOrm()
        return JsonResponse(orm.get_categories_list(), safe=False)

    def retrieve(self, request, *args, **kwargs):
        orm = CustomOrm()
        category = orm.get_category_file(kwargs["pk"])
        if category:
            return JsonResponse(category, safe=False)
        return HttpResponse(
            data='{"message": "Невозможно получить данные, категория не существует." }',
            status=404,
        )
