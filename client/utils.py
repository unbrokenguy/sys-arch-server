import json
import random
import string


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


class Tools:
    @staticmethod
    def print_ok_message(text):
        print(f"{Colors.OKGREEN}{text}{Colors.ENDC}")

    @staticmethod
    def handle_response(response):
        response = json.loads(response.text)
        if response["status"] == "success":
            Tools.print_ok_message(response["message"])
            return True
        if response["status"] == "fail":
            Tools.print_error(response["message"])
            return False

    @staticmethod
    def print_error(text):
        print(f"{Colors.FAIL}{text}{Colors.BOLD}{Colors.ENDC}")

    @staticmethod
    def print_choose_dict(data):
        print("Какое действие вы хотите сделать? (Ответ пишите в виде цифры)")
        for d in sorted(data.keys()):
            print(f"{int(d)}) {data[d]}.")

    @staticmethod
    def get_choose_dict(data):
        return {str(i): data["choose"][i] for i in range(len(data["choose"]))}

    @staticmethod
    def random_string():
        return "".join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(5)
        )
