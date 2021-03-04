import requests


class ServerApi:

    csrftoken = ""

    def __init__(self, url):
        self.url = url + "/api"
        self.client = requests.session()
        self.base_headers = {"accept": "application/json"}

    def get_categories(self):
        response = requests.get(f"{self.url}/category/")
        return response

    def get_category_data(self, category_id):
        response = self.client.get(f"{self.url}/category/{category_id}/")
        return response

    def get_file(self, file_id):
        response = requests.get(f"{self.url}/file/{file_id}/")
        return response

    def get_user_input(self, user_input_id):
        response = self.client.get(
            url=f"{self.url}/user_input/{user_input_id}/",
            headers=self.base_headers,
        )
        return response

    def create_file(self, file):
        response = self.client.post(
            url=f"{self.url}/file/",
            headers=dict.copy(self.base_headers).update(
                {"Content-Type": "multipart/form-data"}
            ),
            data={},
            files=file,
        )
        return response

    def create_user_input(self, value):
        response = self.client.post(
            url=f"{self.url}/user_input/",
            headers=dict.copy(self.base_headers).update(
                {"Content-Type": "application/json"}
            ),
            data={"value": value},
        )
        return response
