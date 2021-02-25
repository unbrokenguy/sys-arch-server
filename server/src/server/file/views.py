from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from file.forms import UploadFileForm
import os
from pathlib import Path

FILE_TYPES = {}


def process_file_type(file_type):
    return file_type


@csrf_exempt
def file_upload(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            file_name = request.FILES["file"].name
            p = Path(f'../../files/{form.cleaned_data["file_type"]}')
            p.mkdir(parents=True, exist_ok=True)
            if not os.path.isfile(f"{p}/{file_name}"):
                with open(f"{p}/{file_name}", "wb+") as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                return JsonResponse(
                    data={"status": "success", "message": "Файл загружен успешно."}
                )
            else:
                return JsonResponse(
                    data={
                        "status": "fail",
                        "message": "Файл с таким именем уже загружен.",
                    }
                )
        else:
            return JsonResponse(data={"status": "fail", "message": "Неверные данные."})


@csrf_exempt
def file_download(request):
    if request.method == "GET":
        file_type = request.GET.get("file_type")
        file_name = request.GET.get("file_name")
        if file_type is None and file_name is None:
            return JsonResponse(data={"choose": os.listdir("../../files/")})
        if file_type is not None and file_name is None:
            return JsonResponse(
                data={"choose": os.listdir(f"../../files/{file_type}/")}
            )

        try:
            return FileResponse(open(f"../../files/{file_type}/{file_name}", "rb"))
        except IOError:
            return JsonResponse(
                data={"status": "fail", "message": "Запрашиваемый файл не существует."}
            )
