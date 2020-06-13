from starlette.requests import Request
from fastapi import APIRouter, HTTPException, Depends
from aiohttp import ClientSession
from datetime import timedelta
from sqlalchemy.orm import Session
from app import exceptions
from app.database.crud import create_token, create_user, get_user_by_social_id, update_token
from app.database.base import get_db
from app.database import schemas
from app.auth.oauth import oauth, authenticate_user, create_access_token
import os


router = APIRouter()

access_token_expire = timedelta(
    minutes=int(os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'])
)


@router.get("/login")
async def login(request: Request):
    if os.environ['NODE_ENV'] == 'development':
        redirect_uri = 'http://192.168.10.19:5919/api/oauth/auth'
    else:
        redirect_uri = request.url_for('auth')
    return await oauth.twitter.authorize_redirect(request, redirect_uri)


@router.get('/auth')
async def auth(request: Request, db: Session = Depends(get_db)):
    token = await oauth.twitter.authorize_access_token(request)
    print(token)
    if (user := await authenticate_user(token['oauth_token'], token['oauth_token_secret'])):
        access_token = create_access_token(
            user["user_id"], access_token_expire)
        if (db_user := get_user_by_social_id(db, user['user_id'])):
            update_token(
                db, db_user, access_token['refresh_token']
            )
        else:
            db_user = create_user(
                db, schemas.UserCreate(username=user["user_name"]))
            usertoken = create_token(db, schemas.TokenCreate(
                social_id=user['user_id'],
                social_name=user['user_name'],
                refresh_token=access_token['refresh_token'],
            ), owner_id=db_user.id)
        return access_token
    else:
        raise exceptions.InvalidTokenException()
