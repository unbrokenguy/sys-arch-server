import json
import os

import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse


@csrf_exempt
def auth(request, method):
    if request.method == "POST":
        credentials = {}
        if method == "sign_in":
            credentials = {"email": request.POST["email"], "password": request.POST["password"]}
        elif method == "sign_up":
            credentials = {"email": request.POST["email"], "password": request.POST["password"],
                           "first_name": request.POST["first_name"], "last_name": request.POST["last_name"]}
        res = requests.post(url=f"http://{os.getenv('AUTH_APP_IP')}/api/auth/{method}/", data=credentials, headers=request.headers)
        if res.status_code == 200:
            return JsonResponse(data=json.loads(res.text), status=200)
        else:
            return HttpResponse(res.text, status=res.status_code)
    else:
        return HttpResponse(status=404)
