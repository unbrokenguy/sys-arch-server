from io import BytesIO
from random import randint

import factory
from PIL import Image
from factory.django import DjangoModelFactory
from rest_api.models import UserInput, Category, File
from django.core.files.base import ContentFile


class CategoryFactory(DjangoModelFactory):
    name = factory.Sequence(lambda _: "Imaginary")

    class Meta:
        model = Category


class UserInputFactory(DjangoModelFactory):
    category = factory.SubFactory(CategoryFactory)
    data = factory.Faker("sentence")

    class Meta:
        model = UserInput


class FileFactory:
    category = factory.SubFactory(CategoryFactory)

    class Meta:
        model = File


class ImageFactory(DjangoModelFactory):
    @classmethod
    def get_image(cls, name="trial", extension="png", size=None):
        if size is None:
            width = randint(20, 1000)
            height = randint(20, 1000)
            size = (width, height)

        color = (256, 0, 0)

        file_obj = BytesIO()
        image = Image.new("RGBA", size=size, color=color)
        image.save(file_obj, extension)
        file_obj.seek(0)
        return ContentFile(file_obj.read(), f"{name}.{extension}")
