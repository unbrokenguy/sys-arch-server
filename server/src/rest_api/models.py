from django.db import models
from rest_api.utils import file_upload


class Category(models.Model):

    name = models.CharField(max_length=255, unique=True, blank=False)


class File(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    file = models.FileField(upload_to=file_upload, null=False)


class UserInput(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    value = models.CharField(max_length=1000)
