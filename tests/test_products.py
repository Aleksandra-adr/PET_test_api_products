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


@pytest.mark.parametrize("username, password", [("admin", "wrong"),
                                                ("Alele", "Test2026"),
                                                (" ", "admin123"),
                                                ("admin", " ")])
def test_invalid_creadentials(api_client, username, password):
    data = {
        "username": username,
        "password": password
    }
    response = api_client.post("/auth/login", json=data)
    assert response.status_code == 401, f"Ожидали 401 ошибку, поулчили {response.status_code}"


@pytest.mark.parametrize("data", [{"password": "admin123"},
                                  {"username": "admin"},
                                  {}])
def test_missing_fieled(api_client, data):
    response = api_client.post("/auth/login", json=data)
    assert response.status_code == 400, f"Ожидали 400 код. получили {response.status_code}"
    assert response.json()["code"] == "MISSING_FIELD"


def test_protected_endpoint_with_garbage_token(api_client):
    response = api_client.post(
        "/products",
        json={"name": "x", "price": 1},
        headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHORIZED"


def test_sort_products_by_price_asc(api_client, seed_products):
    response = api_client.get("/products", params={"sort": "price_asc"})
    data = response.json()
    seed = {i["id"] for i in seed_products}
    filter_data = [i for i in data if i["id"] in seed]
    finish = [i["price"] for i in filter_data]
    assert finish == [2, 15, 56], f"Ожидали сортировку по возростанию , получили {filter_data}"

@pytest.mark.parametrize("sort_value, field, expected", [
                             ("price_asc", "price", [2, 15, 56]),
                              ("price_desc", "price", [56, 15, 2]),
                             ("name_asc", "name", ["банан", "чебурек", "яблоко"]),
                             ("name_desc", "name", ["яблоко", "чебурек", "банан"])])
def test_sort_products(api_client, seed_products, sort_value, field, expected):
    response = api_client.get("/products", params={"sort": sort_value})
    data = response.json()
    seed = {i["id"] for i in seed_products}
    filter_data = [i for i in data if i["id"] in seed]
    finish = [i[field] for i in filter_data]
    assert finish == expected


