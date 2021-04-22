import os
import re
from abc import ABC, abstractmethod
from typing import Type

import requests
from django.http import JsonResponse, HttpResponse
from rest_framework import viewsets, mixins
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_api.serializers import DataSerializer, CategorySerializer
from rest_api.db import DataBase
from rest_api.utils import guess_file_category


class UploadStrategy(ABC):
    """
    Upload strategy interface
    """

    @abstractmethod
    def upload(self, request):
        pass


class FileUploadStrategy(UploadStrategy):
    """
    Upload strategy implementation
    """

    def upload(self, request):
        """Creates file in a database
        Returns:
            Data: Data object or None
        """
        _name = request.FILES["data"].name
        _category, _content_type = guess_file_category(_name)
        _data = request.FILES["data"].read()
        data = DataBase.create_data(_data, _category, _content_type)
        return data


class UserInputUploadStrategy(UploadStrategy):
    """
    Upload strategy implementation
    """

    def upload(self, request):
        """Creates user_input in a database
        Returns:
            Data: Data object or None
        """
        _data = request.data["data"]
        _category = "Числа" if re.match(r"^[-+]?\d+([.,]\d+)?$", _data) else "Строки"
        data = DataBase.create_data(data=_data, category=_category, content_type="plain/text")
        return data


def is_authenticated(func):
    """
    Function decorator that checks if request was made by authorized User
    """

    def wrapper(self, request, *args, **kwargs):
        """
        Checks if "Authorization" header is present in request.
        If header is present tries to retrieve user by token from authorization server.
        So if response status is OK executes the function that the user wants to execute.
        Returns:
             Result of function that the user wants to execute or 401 if user not authorized.
        """
        if "Authorization" in request.headers:
            response = requests.get(url=f"http://{os.getenv('AUTH_APP_IP')}/api/user/", headers=request.headers)
            if response.status_code == 200:
                return func(self, request, *args, **kwargs)
        return HttpResponse(status=401)

    return wrapper


def choose_strategy(request) -> Type[UploadStrategy]:
    """Picking strategy of creating data by type
    Args:
        request (HttpRequest): request With simple fDataBase where "data" field contains String or File

    Returns:
        UploadStrategy: One of the implementation of the UploadStrategy
    """
    if request.FILES.get("data"):
        return FileUploadStrategy
    elif request.data.get("data"):
        return UserInputUploadStrategy
    raise KeyError


class DataViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin):
    parser_classes = (
        FormParser,
        MultiPartParser,
    )
    permission_classes = [AllowAny]
    serializer_class = DataSerializer

    @is_authenticated
    def retrieve(self, request, *args, **kwargs):
        """GET method (<api>/data/{pk}/) that retrieve data by pk

        Returns:
             HttpResponse: HttpResponse with data if it was found or with status 404 and message
        """
        checking = DataBase.get_category_file(kwargs["pk"])
        data, content_type = DataBase.get_data_by_id_and_delete(kwargs["pk"])
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

    @is_authenticated
    def create(self, request, *args, **kwargs):
        """POST method (<api>/data/) that creates data by strategy
        Args:
            request (HttpRequest): request With simple fDataBase where "data" field contains String or File

        Returns:
            HttpResponse: Response with data in json or 404
        """
        try:
            strategy = choose_strategy(request)
            data = strategy().upload(request)
            if data:
                return JsonResponse({"id": data.id, "category": data.category})
            else:
                return HttpResponse(
                    '{"message": "Невозможно создать запись, запись такой категории уже существует." }',
                    status=400,
                )
        except KeyError:
            return HttpResponse(status=400)


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
        """GET method (<api>/category/{pk}/) that retrieve category by pk
        Returns:
            ReHttpResponse: response with category in json if it was found or 404
        """
        category = DataBase.get_category_file(kwargs["pk"])
        if category:
            return JsonResponse([{"id": category[0].id, "name": category[0].category}], safe=False)
        else:
            return HttpResponse(
                '{"message": "Невозможно получить данные, категория не существует." }',
                status=404,
            )
