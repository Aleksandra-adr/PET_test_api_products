from http.client import responses

import pytest


def test_get_products_list(api_client):
    response = api_client.get("/products")
    response_data = response.json()
    assert response.status_code == 200, f"Ожидали статус код 200, получили {response.status_code}"
    assert isinstance(response_data, list), f"Ожидали тело ответа в List, получили {response_data}"

def test_create_product(api_client, auth_headers, cleanup_products):
    data = {
        "name": "батон",
        "price": 55.99
    }
    response = api_client.post("/products", json=data, headers=auth_headers)
    assert response.status_code == 201, f"Ожидали 201 код, пришел {response.status_code}"
    response_data = response.json()
    assert response_data["name"] == data["name"],  f"Ожидали {data["name"]}, поступил {response_data}"
    assert response_data["price"] == data["price"],  f"Ожидали {data["price"]}, поступил {response_data}"
    cleanup_products.append(response_data["id"])

