from django.http import JsonResponse, HttpResponse
from rest_framework import viewsets, mixins
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_api.serializers import DataSerializer
from rest_api.db import DataBase
from rest_api.views.authentication import is_authenticated
from rest_api.views.strategies.utils import choose_strategy


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
            response = HttpResponse()
            response.write(data.ldata)
            response["Content-Type"] = data.content_type
            response["Content-Disposition"] = f'attachment; filename="{data.name}"'
            return response
        elif checking:
            return HttpResponse(
                '{"message": "Невозможно получить запись, запись уже была получена." }',
                status=404,
            )
        return HttpResponse(
            '{"message": "Невозможно получить запись, не сущесвует." }',
            status=404,
        )

    @is_authenticated
    def create(self, request, *args, **kwargs):
        """POST method (<api>/data/) that creates data by strategy
        Args:
            request (HttpRequest): request With simple fDataBase where "data" field contains String or File
        Returns:
            HttpResponse: Response with data in json.
            400 with message if file category already exists or request body does not contain data.
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
            return HttpResponse('{"message": "Невозможно создать запись, неверный запрос." }', status=400)
