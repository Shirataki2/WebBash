from app.main_fastapi import api
from fastapi.testclient import TestClient

client = TestClient(api)


def test_ping():
    resp = client.get('/ping')
    assert resp.status_code == 200
    assert resp.json() == {'status': 'API Server Working'}
