from app.main_fastapi import api
from fastapi.testclient import TestClient
from time import sleep
from concurrent import futures
import asyncio

client = TestClient(api)


def test_ping():
    resp = client.get('/ping')
    assert resp.status_code == 200
    assert resp.json() == {'status': 'API Server Working'}


def test_images_return_404_access_to_not_exist():
    resp = client.get('/images/none.png')
    assert resp.status_code == 404


def test_run_return_422_without_source():
    resp = client.post('/run', {})
    assert resp.status_code == 422


def test_run_ls():
    resp = client.post('/run', {
        'source': f'unko.shout unko|textimg -s;yes {"F"*40}',
    }, headers={"X-Forwarded-For": "192.168.0.5"})
    assert resp.status_code == 200
    assert 'stdout' in resp.json().keys()
    assert resp.json()['exit_code'] == '0'
    resp = client.get(resp.json()['images'][0].replace('/api', ''))
    assert resp.status_code == 200


def test_get_redoc():
    resp = client.get('/docs')
    assert resp.status_code == 200


# def test_run_timeout():
#     resp = client.post('/run', {
#         'source': 'sleep 30',
#     }, headers={"X-Forwarded-For": "192.168.0.5"})
#     assert resp.status_code == 200
#     assert 'stdout' in resp.json().keys()
#     assert resp.json()['stdout'] == ''
#     assert resp.json()['exit_code'] == ''
#     assert resp.json()['exec_sec'] == 'Timeout'
