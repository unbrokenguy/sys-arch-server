from pathlib import Path
import requests
import json
import os


class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def handle_response(response):
    response = json.loads(response.text)
    if response["status"] == "success":
        print_ok_message(response["message"])
        return True
    if response["status"] == "fail":
        print_error(response["message"])
        return False


def print_ok_message(text):
    print(f"{Colors.OKGREEN}{text}{Colors.ENDC}")


def print_error(text):
    print(f"{Colors.FAIL}{text}{Colors.BOLD}{Colors.ENDC}")


def print_choose_dict(data):
    print("0) Выход.")
    for d in sorted(data.keys()):
        print(f"{int(d)}) {data[d]}.")


def get_choose_dict(data):
    return {str(i + 1): data["choose"][i] for i in range(len(data["choose"]))}


class FileManager:
    def __init__(self, url):
        p = Path("/files/")
        p.mkdir(parents=True, exist_ok=True)
        self.url = url

    def exit(self):
        print_ok_message("Выход из приложения.")
        exit()

    def start(self):
        print(
            "Какое действие вы хотите сделать? (Ответ пишите в виде цифры)\n\t\
        0) Выход.\n\t\
        1) Свободный ввод.\n\t\
        2) Загрузить файл на сервер.\n\t\
        3) Загрузить файл с сервера."
        )

        user_input = input()
        if user_input == "1":
            self.user_input_upload()
        elif user_input == "2":
            self.upload()
        elif user_input == "3":
            self.download()
        elif user_input == "0":
            self.exit()
        else:
            print_error("Пожалуйста введите корректные данные.")

    def upload(self):
        print(
            "Выберите файл для загрузки (Укажите абсолютный путь)\nЧтобы выйти введите 0."
        )
        path = input()
        if path == "0":
            self.exit()
        if os.path.isfile(path):
            self.file_upload(path)
            self.start()
        else:
            print_error(f"Не является файлом {path}")
            self.upload()

    def user_input_upload(self):
        print("Введите данные.")
        data = {
            # "description": "MY AWESOME FILE",
            "user_input": input()
        }
        r = requests.post(url=f"{self.url}/upload/", headers={}, data=data)
        handle_response(r)
        self.start()

    def file_upload(self, path):
        data = {
            "description": "MY AWESOME FILE",
        }
        files = {"file": open(path, "rb")}
        r = requests.post(url=f"{self.url}/upload/", headers={}, data=data, files=files)
        handle_response(r)
        self.start()

    def download(self):
        print("Выберите категорию:")
        r = requests.get(url=f"{self.url}/download")
        file_types = get_choose_dict(json.loads(r.text))
        print_choose_dict(file_types)
        user_input = input()
        if user_input == "0":
            self.exit()
        if user_input not in file_types.keys():
            print_error("Не является категорией")
            self.download()
        self.download_file(file_types[user_input])

    def download_file(self, file_type):
        print("Выберите:")
        r = requests.get(url=f"{self.url}/download?file_type={file_type}")
        files = get_choose_dict(json.loads(r.text))
        print_choose_dict(files)
        user_input = input()
        if user_input == "0":
            self.exit()
        if user_input not in files.keys():
            print_error("Не допустимое значение.")
            self.download_file(file_type)
        self.file_download(file_type, files[user_input])
        self.start()

    def file_download(self, file_type, file_name):
        r = requests.get(
            url=f"{self.url}/download?file_type={file_type}&file_name={file_name}",
            stream=True,
        )
        if "status" in r.text:
            handle_response(r)
        elif "data" in r.text:
            data = json.loads(r.text)
            print_ok_message("Данные успешно получены.")
            p = Path(f"files/{file_type}/")
            p.mkdir(parents=True, exist_ok=True)
            if not os.path.isfile(f"{p}/{file_name}"):
                with open(f"{p}/{file_name}", "wb+") as destination:
                    print(data["data"])
        else:
            if r.status_code == 200:
                p = Path(f"files/{file_type}/")
                p.mkdir(parents=True, exist_ok=True)
                if not os.path.isfile(f"{p}/{file_name}"):
                    with open(f"{p}/{file_name}", "wb+") as destination:
                        for chunk in r:
                            destination.write(chunk)
                print_ok_message(f"Файл успешно загружен в {p}/{file_name}")


manager = FileManager("http://127.0.0.1:8000")
print(manager.url)
manager.start()
