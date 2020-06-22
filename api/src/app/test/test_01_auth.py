from fastapi.testclient import TestClient
from time import sleep
from concurrent import futures
from urllib.parse import urljoin
import pytest
import app.main_fastapi
from app.database.crud import create_token, create_user, get_user_by_social_id, update_token
from app.database.base import get_db
from app.database import schemas
from app.auth.oauth import oauth, authenticate_user, create_access_token
from datetime import timedelta
import asyncio
import os


client = TestClient(app.main_fastapi.api)

# TODO: テスト時にあらかじめTwitter Userを作っとかないとデプロイ時のテストには通らん...


@pytest.fixture
async def access_token():
    # REGISTER Token
    access_token_expire = timedelta(
        minutes=int(os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'])
    )
    db = next(get_db())
    if (user := await authenticate_user(os.environ['TWITTER_ACCESS_TOKEN'], os.environ['TWITTER_ACCESS_TOKEN_SECRET'])):
        access_token = create_access_token(
            user["user_id"], access_token_expire)
        if (db_user := get_user_by_social_id(db, user['user_id'])):
            update_token(
                db, db_user, access_token['refresh_token']
            )
        else:
            db_user = create_user(
                db, schemas.UserCreate(username=user["user_name"], avater_url=user["avater_url"]))
            usertoken = create_token(db, schemas.TokenCreate(
                social_id=user['user_id'],
                refresh_token=access_token['refresh_token'],
            ), owner_id=db_user.id)
        return access_token
    else:
        assert False
    # GET Token
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
        "access-token": access_token['access_token'].decode('utf-8')
    })
    assert resp.status_code == 200


def test_invalid_token():
    resp = client.post('/token/', data={
        'oauth_token': os.environ['TWITTER_ACCESS_TOKEN'][:-1],
        'oauth_token_secret': os.environ['TWITTER_ACCESS_TOKEN_SECRET'],
    })
    assert resp.status_code == 401
    assert resp.json()['detail'] == 'Requested token is invalid.'
