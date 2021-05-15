from typing import Type

from rest_api.views.strategies.upload import FileUploadStrategy, UserInputUploadStrategy, UploadStrategy


def choose_strategy(request) -> Type[UploadStrategy]:
    """Picking strategy of creating data by type
    Args:
        request (HttpRequest): request With simple fDataBase where "data" field contains String or File

    Returns:
        UploadStrategy: One of the implementation of the UploadStrategy
    """
    if request.FILES.get("data"):
        return FileUploadStrategy
    elif request.data.get("data"):
        return UserInputUploadStrategy
    raise KeyError
