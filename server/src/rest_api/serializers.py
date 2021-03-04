from rest_framework import serializers
from rest_api.models import File
from rest_api.models import UserInput
from rest_api.models import Category
from rest_api.utils import guess_file_category


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ("id", "file")

    def create(self, validated_data):
        category, created = Category.objects.get_or_create(
            name=guess_file_category(validated_data["file"].name)
        )
        file = File(file=validated_data["file"], category=category)
        file.save()
        return file


class UserInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInput
        fields = ("id", "value")

    def create(self, validated_data):
        category, created = Category.objects.get_or_create(name="Ручной ввод")
        user_input = UserInput(value=validated_data["value"], category=category)
        user_input.save()
        return user_input


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")
