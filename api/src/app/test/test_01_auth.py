from fastapi.testclient import TestClient
from time import sleep
from concurrent import futures
from urllib.parse import urljoin
import pytest
import app.main_fastapi
import asyncio
import os


client = TestClient(app.main_fastapi.api)


@pytest.fixture
def access_token():
    resp = client.post('/token/', data={
        'oauth_token': os.environ['TWITTER_ACCESS_TOKEN'],
        'oauth_token_secret': os.environ['TWITTER_ACCESS_TOKEN_SECRET'],
    })
    assert resp.status_code == 200
    assert 'access_token' in resp.json().keys()
    assert 'refresh_token' in resp.json().keys()
    return resp.json()['access_token']


def test_access_user(access_token):
    resp = client.get('/users/me', headers={
        "access-token": access_token
    })
    assert resp.status_code == 200


def test_invalid_token():
    resp = client.post('/token/', data={
        'oauth_token': os.environ['TWITTER_ACCESS_TOKEN'][:-1],
        'oauth_token_secret': os.environ['TWITTER_ACCESS_TOKEN_SECRET'],
    })
    assert resp.status_code == 401
    assert resp.json()['detail'] == 'Requested token is invalid.'
