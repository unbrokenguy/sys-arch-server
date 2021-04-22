from rest_framework import serializers
from rest_api.models import Category, Data


class DataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Data
        fields = ("id", "data")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")
