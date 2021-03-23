import os
import re

import requests
from django.http import JsonResponse, HttpResponse
from rest_framework import viewsets, mixins
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_api.serializers import UserInputSerializer, FileSerializer, CategorySerializer
from rest_api.models import File, Category
from rest_api.custom_orm import CustomOrm
from rest_api.utils import guess_file_category
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


def is_authenticated(func):
    def wrapper(self, request, *args, **kwargs):
        if os.getenv("TEST"):
            return func(self, request, *args, **kwargs)
        if "Authorization" in request.headers:
            response = requests.get(
                url=f"http://{os.getenv('AUTH_APP_IP')}/api/user/", headers=request.headers
            )
            if response.status_code == 200:
                return func(self, request, *args, **kwargs)
        return HttpResponse(status=404)

    return wrapper


class DataViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin):
    parser_classes = (
        FormParser,
        MultiPartParser,
    )
    permission_classes = [AllowAny]
    serializer_class = FileSerializer
    @is_authenticated
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
                '{"message": "Невозможно получить запись, запись уже была получена." }',
                status=404,
            )
        return HttpResponse(
            '{"message": "Невозможно получить запись, запись не сущесвует." }',
            status=404,
        )

    def create(self, request, *args, **kwargs):
        orm = CustomOrm()
        try:
            _name = request.FILES["data"].name
            _category, _content_type = guess_file_category(_name)
            _data = request.FILES["data"].read()
            data = orm.create_data(_data, _category, _content_type)
            if data:
                return JsonResponse({"id": data.id, "category": data.category})
            else:
                return HttpResponse(
                    '{"message": "Невозможно создать запись, запись такой категории уже существует." }',
                    status=400,
                )
        except Exception:
            _data = request.data["data"]
            _category = "Числа" if re.match(r"^[-+]?\d+([.,]\d+)?$", _data) else "Строки"
            data = orm.create_data(data=_data, category=_category, content_type="plain/text")
            if data:
                return JsonResponse({"id": data.id, "category": data.category})
            else:
                return HttpResponse(
                    '{"message": "Невозможно создать запись, запись такой категории уже существует." }',
                    status=400,
                )



class FileViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    parser_classes = (
        FormParser,
        MultiPartParser,
    )
    permission_classes = [AllowAny]
    queryset = File.objects.all()
    serializer_class = FileSerializer

    @is_authenticated
    def create(self, request, *args, **kwargs):
        orm = CustomOrm()
        _name = request.FILES["data"].name
        _category, _content_type = guess_file_category(_name)
        _data = request.FILES["data"].read()
        data = orm.create_data(_data, _category, _content_type)
        if data:
            return JsonResponse({"id": data.id, "category": data.category})
        else:
            return HttpResponse(
                '{"message": "Невозможно создать запись, запись такой категории уже существует." }',
                status=400,
            )


class UserInputViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    permission_classes = [AllowAny]
    serializer_class = UserInputSerializer

    @is_authenticated
    def create(self, request, *args, **kwargs):
        orm = CustomOrm()
        _data = request.data["data"]
        _category = "Числа" if re.match(r"^[-+]?\d+([.,]\d+)?$", _data) else "Строки"
        data = orm.create_data(data=_data, category=_category, content_type="plain/text")
        if data:
            return JsonResponse({"id": data.id, "category": data.category})
        else:
            return HttpResponse(
                '{"message": "Невозможно создать запись, запись такой категории уже существует." }',
                status=400,
            )


class CategoryViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    permission_classes = [AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @is_authenticated
    def list(self, request, *args, **kwargs):
        orm = CustomOrm()
        return JsonResponse(orm.get_categories_list(), safe=False)

    @is_authenticated
    def retrieve(self, request, *args, **kwargs):
        orm = CustomOrm()
        category = orm.get_category_file(kwargs["pk"])
        if category:
            return JsonResponse(category, safe=False)
        else:
            return HttpResponse(
                '{"message": "Невозможно получить данные, категория не существует." }',
                status=404,
            )
