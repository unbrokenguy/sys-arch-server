import pytest
from rest_framework import status

from rest_api.tests.factories.factory import UserInputFactory, ImageFactory
from rest_api.custom_orm import CustomOrm


@pytest.mark.django_db
def test_user_input_upload_success(api_client):
    user_input = UserInputFactory.create()
    response = api_client.post("/api/user_input/", data={"data": user_input.data})
    orm = CustomOrm()
    _data = orm.get_data_by_id_and_delete(data_id=response.json()['id'])
    assert response.status_code == status.HTTP_200_OK
    assert _data[0] == bytes(user_input.data, encoding="utf-8")


@pytest.mark.django_db
def test_user_input_upload_fail(api_client):
    user_input = UserInputFactory.create()
    orm = CustomOrm()
    _data = orm.create_data(data=user_input.data, category="Строки", content_type="plain/text")
    response = api_client.post("/api/user_input/", data={"data": user_input.data})
    _data = orm.get_data_by_id_and_delete(data_id=_data.id)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_category_list_success(api_client):
    user_input = UserInputFactory.create()
    orm = CustomOrm()
    _data = orm.create_data(data=user_input.data, category="Строки", content_type="plain/text")
    response = api_client.get("/api/category/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == len(orm.get_categories_list())
    _data = orm.get_data_by_id_and_delete(data_id=_data.id)
