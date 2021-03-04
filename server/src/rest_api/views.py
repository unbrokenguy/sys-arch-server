from django.http import JsonResponse, FileResponse
from django.core import serializers
from rest_framework import viewsets, mixins
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_api.serializers import UserInputSerializer, FileSerializer, CategorySerializer
from rest_api.models import UserInput, File, Category


class FileViewSet(
    viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin
):
    parser_classes = (
        FormParser,
        MultiPartParser,
    )
    permission_classes = [AllowAny]
    queryset = File.objects.all()
    serializer_class = FileSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        file = self.get_object()
        actual_file = open(file.file.path, 'rb')
        response = FileResponse(actual_file)
        file.file.delete()
        file.delete()
        return response


class UserInputViewSet(
    viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin
):
    permission_classes = [AllowAny]
    queryset = UserInput.objects.all()
    serializer_class = UserInputSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        user_input = self.get_object()
        user_input_id = user_input.pk
        user_input_value = user_input.value
        user_input.delete()
        return JsonResponse({'id': user_input_id, 'value': user_input_value}, safe=False)


class CategoryViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    permission_classes = [AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def retrieve(self, request, *args, **kwargs):
        files = File.objects.filter(category=self.get_object())
        user_input = UserInput.objects.filter(category=self.get_object())
        if files:
            raw_data = serializers.serialize('python', files)
            data = [
                {'id': d['pk'], 'value': str(d['fields']['file']).split('/')[1]}
                for d in raw_data
            ]
        else:
            raw_data = serializers.serialize('python', user_input)
            data = [{'id': d['pk'], 'value': d['fields']['value']} for d in raw_data]
        return JsonResponse(data, safe=False)
