from django.http import JsonResponse, FileResponse, HttpResponse
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt
from file.forms import UploadFileForm
import os
from pathlib import Path
import mimetypes
from file.file_types import FILE_TYPES
from server.settings import MEDIA_ROOT
import re


@csrf_exempt
def file_download(request):
    if request.method == "GET":
        file_category = request.GET.get("file_type")
        file_name = request.GET.get("file_name")
        if file_category is None and file_name is None:
            return category_list()
        if file_category is not None and file_name is None:
            return files_list(file_category)
        if file_category is not None and file_name is not None:
            return handle_download(file_category, file_name)
    else:
        return HttpResponse(status=405)


@csrf_exempt
def file_upload(request):
    if request.method == "POST":
        # TODO: Split to UploadFileForm and UploadUserInputForm
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            user_input = request.POST.get("user_input", None)
            if user_input is not None:
                return handle_user_input(user_input)
            else:
                return handle_file_upload(request)
        else:
            return json_status_response(status="fail", message="Неверные данные.")
    else:
        return HttpResponse(status=405)


def json_status_response(status, message):
    return JsonResponse(
        data={
            "status": f"{status}",
            "message": f"{message}",
        }
    )


def guess_file_category(file):
    if "user_input_" in file:
        file_type = file
    else:
        file_name = file.name
        file_type = mimetypes.guess_type(file_name)[0]
    for c in FILE_TYPES.keys():
        if file_type in FILE_TYPES[c]:
            return c
    return file_type


def save_user_input(file_type, file_name, user_input):
    p = Path(f"{MEDIA_ROOT}/{file_type}")
    p.mkdir(parents=True, exist_ok=True)
    with open(f"{p}/{file_name}", "a") as destination:
        destination.write(f"{user_input}\n")


def handle_user_input(user_input):
    number_regex = r"^[-+]?\d+([.,]\d+)?$"
    try:
        if re.match(number_regex, user_input) is not None:
            file_category = guess_file_category("user_input_number")
            file_name = "numbers.txt"
            save_user_input(file_category, file_name, user_input)
        else:
            file_category = guess_file_category("user_input_string")
            file_name = "strings.txt"
            save_user_input(file_category, file_name, user_input)
        return json_status_response(status="success", message="Данные загружены успешно.")
    except FileNotFoundError:
        return json_status_response(status="fail", message="Данные загружены не были.")


def save_file(file, path):
    with open(path, "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)


def handle_file_upload(request):
    try:
        file = request.FILES["file"]
        file_category = guess_file_category(file)
        file_name = request.FILES["file"].name
        p = Path(f"{MEDIA_ROOT}/{file_category}")
        p.mkdir(parents=True, exist_ok=True)
        if not os.path.isfile(f"{p}/{file_name}"):
            save_file(file, f"{p}/{file_name}")
            return json_status_response(
                status="success", message="Файл загружен успешно."
            )
        else:
            return json_status_response(
                status="fail", message="Файл с таким именем уже загружен."
            )
    except MultiValueDictKeyError:
        return json_status_response(
            status="fail", message="Файл для загрузки выбран не был."
        )


def data_response(file_path, file_name):
    file = open(file_path, "r")
    lines = file.readlines()
    file.close()
    new_file = open(file_path, "w+")
    exist = False
    for line in lines:
        if line.rstrip() != file_name:
            new_file.write(line)
        else:
            exist = True
    new_file.close()
    if exist:
        return JsonResponse(data={"data": f"{file_name}"})
    else:
        return json_status_response("fail", "Таких данных не существует.")


def data_list_response(file_path):
    file = open(file_path, "r")
    lines = file.readlines()
    file.close()
    return JsonResponse(data={"choose": list(map(lambda x: x.rstrip(), lines))})


def file_response(file_category, file_name):
    try:
        path = f"{MEDIA_ROOT}/{file_category}/{file_name}"
        file = open(path, "rb")
        response = FileResponse(file)
        os.remove(path)
        return response
    except IOError:
        return json_status_response(
            status="fail", message="Запрашиваемый файл не существует."
        )


def files_list_response(file_category):
    return JsonResponse(data={"choose": os.listdir(f"{MEDIA_ROOT}/{file_category}/")})


def numbers_list_response():
    return data_list_response(f"{MEDIA_ROOT}/Числа/numbers.txt")


def strings_list_response():
    return data_list_response(f"{MEDIA_ROOT}/Строки/strings.txt")


def category_list():
    return JsonResponse(data={"choose": os.listdir(MEDIA_ROOT)})


def number_download(file_name):
    file_path = f"{MEDIA_ROOT}/Числа/numbers.txt"
    if re.match(r"^[-+]?\d+([.,]\d+)?$", file_name) is not None:
        return data_response(file_path, file_name)
    else:
        return json_status_response("fail", "Некорректный формат числа.")


def string_download(file_name):
    file_path = f"{MEDIA_ROOT}/Строки/strings.txt"
    return data_response(file_path, file_name)


def files_list(file_category):
    if "Числа" in file_category:
        return numbers_list_response()
    elif "Строки" in file_category:
        return strings_list_response()
    else:
        return files_list_response(file_category)


def handle_download(file_category, file_name):
    if "Числа" in file_category and file_name is not None:
        return number_download(file_name)
    if "Строки" in file_category and file_name is not None:
        return string_download(file_name)
    else:
        return file_response(file_category, file_name)
