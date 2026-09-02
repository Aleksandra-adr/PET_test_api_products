import os
import pytest
import requests


@pytest.fixture
def api_client():
    """Создает апи клиента"""
    base_url = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000")
    session = requests.Session()
    with session:
        yield ApiClient(session, base_url)

class ApiClient:
    def __init__(self, session, base_url):
        self.session = session
        self.base_url = base_url

    def get(self, path, **kwargs):
        return self.session.get(self.base_url + path, **kwargs)

    def post(self, path, **kwargs):
        return self.session.post(self.base_url + path, **kwargs)

    def put(self, path, **kwargs):
        return self.session.put(self.base_url + path, **kwargs)

    def delete(self, path, **kwargs):
        return self.session.delete(self.base_url + path, **kwargs)

@pytest.fixture
def auth_token(api_client):
    """Получает токен"""
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    response = api_client.post("/auth/login", json=login_data)
    assert response.status_code == 200, f"Ожидали статус код 200, получили {response.status_code}"
    data = response.json()
    return data['access_token']

@pytest.fixture
def auth_headers(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers

@pytest.fixture
def cleanup_products(api_client, auth_headers):
    ids = []
    yield ids

    for id in ids:
        api_client.delete(f"/products/{id}", headers=auth_headers)


@pytest.fixture
def seed_products(api_client, auth_headers):
    """Создает товар"""
    products1 = {
        "name": "яблоко",
        "price": 2,
        "description": ""
    }
    products2 = {
        "name": "банан",
        "price": 15,
        "description": ""
    }
    products3 = {
        "name": "чебурек",
        "price": 56,
        "description": ""
    }
    products_to_create = [products1, products2, products3]
    create = []
    for i in products_to_create:
        response = api_client.post(f"/products", json=i, headers=auth_headers)
        create.append(response.json())
    yield create
    for i in create:
        api_client.delete(f"/products/{i['id']}", headers=auth_headers)










