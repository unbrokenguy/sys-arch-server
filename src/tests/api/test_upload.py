import json
import os
import random

import pytest
from faker import Faker
import requests
from rest_framework import status
from rest_api.db import DataBase, Base, engine

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

fake = Faker()
Faker.seed(random.randint(0, 10000))
headers = {"accept": "application/json"}
host_url = f'http://{os.getenv("WEB_IP", "http://localhost:8000")}'


class User:
    def __init__(self):
        self.token = None
        self.email = fake.ascii_safe_email()
        self.password = fake.password()
        self.first_name = fake.first_name()
        self.last_name = fake.last_name()

    def sign_up_credentials(self):
        return {
            "email": self.email,
            "password": self.password,
            "first_name": self.first_name,
            "last_name": self.last_name,
        }

    def sign_in_credentials(self):
        return {"email": self.email, "password": self.password}


user = User()


@pytest.mark.auth
def test_auth_sign_up_success():
    response = requests.post(host_url + "/api/auth/sign_up/", data=user.sign_up_credentials(), headers=headers)
    print(response.text)
    user.token = json.loads(response.text)["auth_token"]
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.auth
def test_auth_sign_in_success():
    response = requests.post(host_url + "/api/auth/sign_in/", data=user.sign_in_credentials(), headers=headers)
    print(response.text)
    _token = json.loads(response.text)["auth_token"]
    headers.update({"Authorization": f"Token {_token}"})
    assert response.status_code == status.HTTP_200_OK
    assert headers.get("Authorization")
    assert user.token == _token


@pytest.mark.django_db
def test_user_input_upload_success():
    user_input = fake.sentence(nb_words=10)
    response = requests.post(host_url + "/api/user_input/", data={"data": user_input}, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    _data = DataBase.get_data_by_id_and_delete(data_id=response.json()["id"])
    assert _data[0] == bytes(user_input, encoding="utf-8")


@pytest.mark.django_db
def test_user_input_upload_fail():
    user_input = fake.sentence(nb_words=10)
    _data = DataBase.create_data(data=user_input, category="Строки", content_type="plain/text", filename="")
    response = requests.post(host_url + "/api/user_input/", data={"data": user_input}, headers=headers)
    _data = DataBase.get_data_by_id_and_delete(data_id=_data.id)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_category_list_success():
    user_input = fake.sentence(nb_words=10)
    _data = DataBase.create_data(data=user_input, category="Строки", content_type="plain/text", filename="")
    response = requests.get(host_url + "/api/category/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == len(DataBase.get_categories_list())
    _data = DataBase.get_data_by_id_and_delete(data_id=_data.id)
