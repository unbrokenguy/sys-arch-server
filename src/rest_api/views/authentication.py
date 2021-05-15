import os
import requests
from django.http import HttpResponse


def is_authenticated(func):
    """
    Function decorator that checks if request was made by authorized User
    """

    def wrapper(self, request, *args, **kwargs):
        """
        Checks if "Authorization" header is present in request.
        If header is present tries to retrieve user by token from authorization server.
        So if response status is OK executes the function that the user wants to execute.
        Returns:
             Result of function that the user wants to execute or 401 if user not authorized.
        """
        if "Authorization" in request.headers:
            response = requests.get(url=f"http://{os.getenv('AUTH_APP_IP')}/api/user/", headers=request.headers)
            if response.status_code == 200:
                return func(self, request, *args, **kwargs)
        return HttpResponse(status=401)

    return wrapper
