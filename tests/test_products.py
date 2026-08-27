import pytest


def test_get_products_list(api_client):
    response = api_client.get("/products")
    response_data = response.json()
    assert response.status_code == 200, f"Ожидали статус код 200, получили {response.status_code}"
    assert isinstance(response_data, list), f"Ожидали тело ответа в List, получили {response_data}"

