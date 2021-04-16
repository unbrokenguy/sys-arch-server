import json

import pytest
import factory
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_api.tests.factories.factory import UserInputFactory
from rest_api.custom_orm import CustomOrm

headers = {"accept": "application/json"}


class User:
    def __init__(self):
        self.token = None
        self.email = factory.Faker('email')
        self.password = factory.LazyFunction(lambda: make_password('pi3.1415'))
        self.first_name = factory.Faker('first_name')
        self.last_name = factory.Faker('last_name')

    def sign_up_credentials(self):
        return {"email": self.email, "password": self.password, "first_name": self.first_name, "last_name": self.last_name}

    def sign_in_credentials(self):
        return {"email": self.email, "password": self.password}


user = User()


@pytest.mark.auth
def test_auth_sign_up_success(api_client):
    response = api_client.post("/api/auth/sign_up/", data=user.sign_up_credentials(), headers=headers)
    user.token = json.loads(response.text)["auth_token"]
    assert response.status_code == status.HTTP_200_OK
    assert headers.get("Authorization")


@pytest.mark.auth
def test_auth_sign_in_success(api_client):
    response = api_client.post("/api/auth/sign_in/", data=user.sign_in_credentials(), headers=headers)
    _token = json.loads(response.text)["auth_token"]
    headers.update({"Authorization": f"Token {_token}"})
    assert response.status_code == status.HTTP_200_OK
    assert headers.get("Authorization")
    assert user.token == _token
    

@pytest.mark.django_db
def test_user_input_upload_success(api_client):
    user_input = UserInputFactory.create()
    response = api_client.post("/api/user_input/", data={"data": user_input.data}, headers=headers)
    orm = CustomOrm()
    _data = orm.get_data_by_id_and_delete(data_id=response.json()["id"])
    assert response.status_code == status.HTTP_200_OK
    assert _data[0] == bytes(user_input.data, encoding="utf-8")


@pytest.mark.django_db
def test_user_input_upload_fail(api_client):
    user_input = UserInputFactory.create()
    orm = CustomOrm()
    _data = orm.create_data(
        data=user_input.data, category="Строки", content_type="plain/text"
    )
    response = api_client.post("/api/user_input/", data={"data": user_input.data})
    _data = orm.get_data_by_id_and_delete(data_id=_data.id)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_category_list_success(api_client):
    user_input = UserInputFactory.create()
    orm = CustomOrm()
    _data = orm.create_data(
        data=user_input.data, category="Строки", content_type="plain/text"
    )
    response = api_client.get("/api/category/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == len(orm.get_categories_list())
    _data = orm.get_data_by_id_and_delete(data_id=_data.id)
