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












