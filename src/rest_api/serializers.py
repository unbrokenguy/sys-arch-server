from rest_framework import serializers
from rest_api.models import File
from rest_api.models import UserInput
from rest_api.models import Category


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ("id", "data")


class UserInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInput
        fields = ("id", "data")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")
