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


@pytest.fixture
async def access_token():  # pragma: no cover
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
    resp['user_id'] = db_user.id
    return resp.json()


@pytest.mark.asyncio
async def test_create_user():  # pragma: no cover
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
    return resp.json()


def test_access_user(access_token):
    resp = client.get('/users/me', headers={
        "access-token": access_token['access_token']
    })
    assert resp.status_code == 200


def test_get_users(access_token):
    resp = client.get('/users/', headers={
        "access-token": access_token['access_token']
    })
    assert resp.status_code == 200


def test_update_user(access_token):
    resp = client.put('/users/me', data={
        "username": "GSGSGS",
    }, headers={
        "access-token": access_token['access_token']
    })
    assert resp.status_code == 204


def test_create_post(access_token):
    resp = client.post('/posts/', json={
        'title': 'hoge',
        'description': 'fuga',
        'main': 'piyo',
        'stdout': 'ooo',
        'stderr': 'ppp',
        'exitcode': 'kfc',
        'posted_images': ['a'],
        'generated_images': ['f'],
    }, headers={
        "access-token": access_token['access_token']
    })
    assert resp.status_code == 204


def test_delete_post(access_token):
    resp = client.post('/posts/', json={
        'title': 'hoge',
        'description': 'fuga',
        'main': 'piyo',
        'stdout': 'ooo',
        'stderr': 'ppp',
        'exitcode': 'kfc',
        'posted_images': ['a'],
        'generated_images': ['f'],
    }, headers={
        "access-token": access_token['access_token']
    })
    assert resp.status_code == 204
    resp = client.get('/users/me/posts', headers={
        "access-token": access_token['access_token']
    })
    assert resp.status_code == 200
    resp = client.delete(f'/users/me/posts/{resp.json()[0]["id"]}', headers={
        "access-token": access_token['access_token']
    })
    assert resp.status_code == 204


def test_refresh_token(access_token):
    resp = client.post('/token/refresh', data={
        "access_token": access_token['access_token'],
        "refresh_token": access_token['refresh_token'],
    })
    assert resp.status_code == 204
    resp = client.post('/token/refresh', data={
        "access_token": access_token['access_token'],
        "refresh_token": access_token['refresh_token'][:-1],
    })
    assert resp.status_code == 401
    resp = client.post('/token/refresh', data={
        "access_token": access_token['access_token'][:-1],
        "refresh_token": access_token['refresh_token'][:-1],
    })
    assert resp.status_code == 401


def test_get_access_token(access_token):
    resp = client.post('/token/', data={
        "oauth_token": os.environ['TWITTER_ACCESS_TOKEN'],
        "oauth_token_secret": os.environ['TWITTER_ACCESS_TOKEN_SECRET'],
    })
    assert resp.status_code == 200
    resp = client.post('/token/', data={
        "oauth_token": os.environ['TWITTER_ACCESS_TOKEN'][:-1]+'l',
        "oauth_token_secret": os.environ['TWITTER_ACCESS_TOKEN_SECRET'],
    })
    assert resp.status_code == 401


def test_verify_token(access_token):
    resp = client.post('/token/verify', data={
        "access_token": access_token['access_token'],
    })
    assert resp.status_code == 200
    resp = client.post('/token/verify', data={
        "access_token": access_token['access_token'][:-1],
    })
    assert resp.status_code == 401


def test_invalid_token():
    resp = client.post('/token/', data={
        'oauth_token': os.environ['TWITTER_ACCESS_TOKEN'][:-1],
        'oauth_token_secret': os.environ['TWITTER_ACCESS_TOKEN_SECRET'],
    })
    assert resp.status_code == 401
    assert resp.json()['detail'] == 'Requested token is invalid.'
