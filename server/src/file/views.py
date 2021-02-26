from django.http import JsonResponse, FileResponse
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt
from file.forms import UploadFileForm
import os
from pathlib import Path
import mimetypes
from file.file_types import FILE_TYPES
from manage import PATH_TO_STORAGE
import re


def process_file_type(file):
    if "user_input_" in file:
        file_type = file
    else:
        file_name = file.name
        file_type = mimetypes.guess_type(file_name)[0]
    for t in FILE_TYPES.keys():
        if file_type in FILE_TYPES[t]:
            return t
    return file_type


def write_str_num_user_input(file_type, file_name, user_input):
    p = Path(f"{PATH_TO_STORAGE}/{file_type}")
    p.mkdir(parents=True, exist_ok=True)
    with open(f"{p}/{file_name}", "a") as destination:
        destination.write(f"{user_input}\n")


@csrf_exempt
def file_upload(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            user_input = request.POST.get("user_input", None)
            if user_input is not None:
                number_regex = r"^[-+]?\d+([.,]\d+)?$"
                try:
                    if re.match(number_regex, user_input) is not None:
                        file_type = process_file_type("user_input_number")
                        file_name = "numbers.txt"
                        write_str_num_user_input(file_type, file_name, user_input)
                    else:
                        file_type = process_file_type("user_input_string")
                        file_name = "strings.txt"
                        write_str_num_user_input(file_type, file_name, user_input)
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
            else:
                try:
                    file = request.FILES["file"]
                    file_type = process_file_type(file)
                    file_name = request.FILES["file"].name
                    p = Path(f"{PATH_TO_STORAGE}/{file_type}")
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

        else:
            return JsonResponse(data={"status": "fail", "message": "Неверные данные."})


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
    return JsonResponse(
        data={"choose": list(map(lambda x: x.rstrip(), lines))}
    )


@csrf_exempt
def file_download(request):
    if request.method == "GET":
        file_type = request.GET.get("file_type")
        file_name = request.GET.get("file_name")
        if file_type is None and file_name is None:
            return JsonResponse(data={"choose": os.listdir(PATH_TO_STORAGE)})
        if file_type is not None and file_name is None:
            if "Числа" in file_type:
                return get_str_num_data_response(f"{PATH_TO_STORAGE}/{file_type}/numbers.txt")
            elif "Строки" in file_type:
                return get_str_num_data_response(f"{PATH_TO_STORAGE}/{file_type}/strings.txt")
            else:
                return JsonResponse(
                    data={"choose": os.listdir(f"{PATH_TO_STORAGE}/{file_type}/")}
                )
        if "Числа" in file_type and file_name is not None:
            file_path = f"{PATH_TO_STORAGE}/{file_type}/numbers.txt"
            if re.match(r"^[-+]?\d+([.,]\d+)?$", file_name) is not None:
                return handle_str_num_response(file_path, file_name)
            else:
                return JsonResponse(
                    data={"status": "fail", "message": "Некорректный формат числа."}
                )
        if "Строки" in file_type and file_name is not None:
            file_path = f"{PATH_TO_STORAGE}/{file_type}/strings.txt"
            return handle_str_num_response(file_path, file_name)
        else:
            try:
                path = f"{PATH_TO_STORAGE}/{file_type}/{file_name}"
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
