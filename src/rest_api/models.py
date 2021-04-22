from django.db import models


class DataField(models.Field):
    """
    Plug for Django automatic processes.
    Custom field.
    """

    description = "String or File"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Category(models.Model):
    """
    Plug for Django automatic processes.
    Describe Category Model.
    """

    name = models.CharField(max_length=255, unique=True, blank=False)


class Data(models.Model):
    """
    Plug for Django automatic processes.
    Describe Data Model.
    """

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    data = DataField()
