from starlette.requests import Request
from fastapi import APIRouter, HTTPException, Depends, Body, Form, Response
from aiohttp import ClientSession
from datetime import timedelta, datetime
from sqlalchemy.orm import Session
from app import exceptions
from app.database.crud import (
    create_token,
    create_user,
    get_user_by_social_id,
    verify_access_token,
    verify_refresh_token,
    TokenStatus,
    update_token
)
from app.database.base import get_db
from app.database import schemas
from app.auth.oauth import oauth, authenticate_user, create_access_token
import os

router = APIRouter()

access_token_expire = timedelta(
    minutes=int(os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'])
)


@router.post('/')
async def token(
    oauth_token: str = Form(...),
    oauth_token_secret: str = Form(...),
    db: Session = Depends(get_db)
):
    if (user := await authenticate_user(oauth_token, oauth_token_secret)):
        if (db_user := get_user_by_social_id(db, user['user_id'])):
            access_token = create_access_token(
                user["user_id"], access_token_expire)
            update_token(
                db, db_user, access_token['refresh_token']
            )
            return access_token
        else:
            raise exceptions.UnauthorizedUserException()
    else:
        raise exceptions.InvalidTokenException()


@router.post('/verify')
async def verify(
    db: Session = Depends(get_db),
    access_token: str = Form(..., media_type='application/json'),
):
    status, data = verify_access_token(db, access_token)
    if status == TokenStatus.VALID:
        return {"detail": "Valid Token", "user_id": data['sub']}
    elif status == TokenStatus.EXPIRED:  # pragma: no cover
        raise exceptions.ExpiredTokenException()
    elif status == TokenStatus.INVALID:
        raise exceptions.InvalidTokenException()


@router.post('/refresh')
async def refresh(
    response: Response,
    access_token: str = Form(...),
    refresh_token: str = Form(...),
    db: Session = Depends(get_db)
):
    status, user = verify_refresh_token(db, access_token, refresh_token)
    if status == TokenStatus.VALID:
        if (db_user := get_user_by_social_id(db, user['sub'])):
            token = create_access_token(
                user["sub"], access_token_expire
            )
            update_token(
                db, db_user, token['refresh_token']
            )
            response.set_cookie("access_token", token['access_token'])
            response.set_cookie("refresh_token", token['refresh_token'])
            response.set_cookie(
                "access_token_expire",
                (token['expires_in'] + datetime.now().timestamp()) * 1000
            )
            return token
        else:
            raise exceptions.UserNotFoundException()
    elif status == TokenStatus.EXPIRED:
        raise exceptions.ExpiredTokenException()
    elif status == TokenStatus.INVALID:
        raise exceptions.InvalidTokenException()
