import json
import os

import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse


@csrf_exempt
def auth(request, method):
    if request.method == "POST":
        credentials = {"email": request.POST["email"], "password": request.POST["password"]}
        res = requests.post(url=f"http://{os.getenv('AUTH_APP_IP')}/api/auth/{method}/", data=credentials)
        if res.status_code == 200:
            return JsonResponse(data=json.loads(res.text), status=200)
        else:
            return HttpResponse(status=res.status_code)
    else:
        return HttpResponse(status=404)
