from django.db import models
from rest_api.utils import file_upload


class DataField(models.Field):
    description = "String or File"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=False)


class Data(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    data = DataField()
