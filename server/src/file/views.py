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


def process_file_category(file):
    if "user_input_" in file:
        file_type = file
    else:
        file_name = file.name
        file_type = mimetypes.guess_type(file_name)[0]
    for c in FILE_TYPES.keys():
        if file_type in FILE_TYPES[c]:
            return c
    return file_type


def write_str_num_user_input(file_type, file_name, user_input):
    p = Path(f"{MEDIA_ROOT}/{file_type}")
    p.mkdir(parents=True, exist_ok=True)
    with open(f"{p}/{file_name}", "a") as destination:
        destination.write(f"{user_input}\n")


def process_user_input(user_input):
    number_regex = r"^[-+]?\d+([.,]\d+)?$"
    try:
        if re.match(number_regex, user_input) is not None:
            file_category = process_file_category("user_input_number")
            file_name = "numbers.txt"
            write_str_num_user_input(file_category, file_name, user_input)
        else:
            file_category = process_file_category("user_input_string")
            file_name = "strings.txt"
            write_str_num_user_input(file_category, file_name, user_input)
        return JsonResponse(
            data={
                "status": "success",
                "message": "Данные загружены успешно.",
            }
        )
    except FileNotFoundError:
        return JsonResponse(
            data={"status": "fail", "message": "Данные загружены не были."}
        )


def process_file_upload(request):
    try:
        file = request.FILES["file"]
        file_category = process_file_category(file)
        file_name = request.FILES["file"].name
        p = Path(f"{MEDIA_ROOT}/{file_category}")
        p.mkdir(parents=True, exist_ok=True)
        if not os.path.isfile(f"{p}/{file_name}"):
            with open(f"{p}/{file_name}", "wb+") as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            return JsonResponse(
                data={
                    "status": "success",
                    "message": "Файл загружен успешно.",
                }
            )
        else:
            return JsonResponse(
                data={
                    "status": "fail",
                    "message": "Файл с таким именем уже загружен.",
                }
            )
    except MultiValueDictKeyError:
        return JsonResponse(
            data={
                "status": "fail",
                "message": "Файл для загрузки выбран не был.",
            }
        )


@csrf_exempt
def file_upload(request):
    if request.method == "POST":
        # TODO: Split to UploadFileForm and UploadUserInputForm
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            user_input = request.POST.get("user_input", None)
            if user_input is not None:
                return process_user_input(user_input)
            else:
                return process_file_upload(request)
        else:
            return JsonResponse(data={"status": "fail", "message": "Неверные данные."})
    else:
        return HttpResponse(status=405)


def handle_str_num_response(file_path, file_name):
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
        return JsonResponse(
            data={"status": "fail", "message": "Таких данных не существует."}
        )


def get_str_num_data_response(file_path):
    file = open(file_path, "r")
    lines = file.readlines()
    file.close()
    return JsonResponse(data={"choose": list(map(lambda x: x.rstrip(), lines))})


def process_file_download(file_category, file_name):
    try:
        path = f"{MEDIA_ROOT}/{file_category}/{file_name}"
        file = open(path, "rb")
        response = FileResponse(file)
        os.remove(path)
        return response
    except IOError:
        return JsonResponse(
            data={
                "status": "fail",
                "message": "Запрашиваемый файл не существует.",
            }
        )


def get_file_categories_or_files(file_category, file_name):
    if file_category is None and file_name is None:
        return JsonResponse(data={"choose": os.listdir(MEDIA_ROOT)})
    if file_category is not None and file_name is None:
        if "Числа" in file_category:
            return get_str_num_data_response(
                f"{MEDIA_ROOT}/{file_category}/numbers.txt"
            )
        elif "Строки" in file_category:
            return get_str_num_data_response(
                f"{MEDIA_ROOT}/{file_category}/strings.txt"
            )
        else:
            return JsonResponse(
                data={"choose": os.listdir(f"{MEDIA_ROOT}/{file_category}/")}
            )
    return None


def handle_download(file_category, file_name):
    if "Числа" in file_category and file_name is not None:
        file_path = f"{MEDIA_ROOT}/{file_category}/numbers.txt"
        if re.match(r"^[-+]?\d+([.,]\d+)?$", file_name) is not None:
            return handle_str_num_response(file_path, file_name)
        else:
            return JsonResponse(
                data={"status": "fail", "message": "Некорректный формат числа."}
            )
    if "Строки" in file_category and file_name is not None:
        file_path = f"{MEDIA_ROOT}/{file_category}/strings.txt"
        return handle_str_num_response(file_path, file_name)
    else:
        return process_file_download(file_category, file_name)


@csrf_exempt
def file_download(request):
    if request.method == "GET":
        file_category = request.GET.get("file_type")
        file_name = request.GET.get("file_name")
        file_categories_or_files = get_file_categories_or_files(file_category, file_name)
        if file_categories_or_files is not None:
            return file_categories_or_files
        return handle_download(file_category, file_name)
    else:
        return HttpResponse(status=405)
