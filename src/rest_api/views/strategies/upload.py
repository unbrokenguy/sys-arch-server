import re

from rest_api.db import DataBase
from rest_api.utils import guess_file_category


class UploadStrategy:
    """
    Upload strategy interface
    """

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
        data = DataBase.create_data(data=_data, category=_category, content_type=_content_type, filename=_name)
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
        data = DataBase.create_data(data=_data, category=_category, content_type="plain/text", filename="")
        return data
