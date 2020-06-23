from starlette.requests import Request
from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.responses import RedirectResponse
from aiohttp import ClientSession
from datetime import timedelta
from sqlalchemy.orm import Session
from datetime import datetime
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
async def login(request: Request):  # pragma: no cover
    if os.environ['NODE_ENV'] == 'development':
        redirect_uri = 'http://192.168.10.19:5919/api/oauth/auth'
    else:
        redirect_uri = request.url_for('auth')
    return await oauth.twitter.authorize_redirect(request, redirect_uri)


@router.get("/logout")
async def logout(response: Response):  # pragma: no cover
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    response.delete_cookie("access_token_expire")
    return


@router.get('/auth')
async def auth(request: Request, response: Response, db: Session = Depends(get_db)):  # pragma: no cover
    try:
        token = await oauth.twitter.authorize_access_token(request)
    except:
        raise exceptions.MissingRequestTokenException()
    if (user := await authenticate_user(token['oauth_token'], token['oauth_token_secret'])):
        access_token = create_access_token(
            user["user_id"], access_token_expire)
        print(token)
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

        if os.environ['NODE_ENV'] == 'development':
            response = RedirectResponse('http://192.168.10.19:4040')
        else:
            response = RedirectResponse('/')
        response.set_cookie("access_token", access_token['access_token'])
        response.set_cookie("refresh_token", access_token['refresh_token'])
        response.set_cookie(
            "access_token_expire",
            (access_token['expires_in'] + datetime.now().timestamp()) * 1000
        )
        return response
    else:
        raise exceptions.InvalidTokenException()
