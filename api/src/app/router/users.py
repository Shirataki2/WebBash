from starlette.requests import Request
from fastapi import APIRouter, HTTPException, Depends, Body, Form, Query, Cookie, Path, File, UploadFile
from aiohttp import ClientSession
from datetime import timedelta
from sqlalchemy.orm import Session
import shutil
import secrets
import aiofiles
from typing import List, Optional
from app import exceptions
from app.database.crud import (
    create_token,
    create_user,
    get_user_by_social_id,
    verify_access_token,
    verify_refresh_token,
    TokenStatus,
    update_token,
    current_user,
    get_users,
    get_user,
    get_user_posts,
    get_user_post
)
from app.database.base import get_db
from app.database import schemas, models
from app.auth.oauth import oauth, authenticate_user, create_access_token
from app.conf import docker_prepare_conf, fastapi_config
import os
import uuid

router = APIRouter()


@router.get('/me', response_model=schemas.User)
async def my_account(
    db: Session = Depends(get_db),
    user: schemas.User = Depends(current_user)
):
    user = get_user(db, user.id)
    return user


@router.put('/me', status_code=204)
async def update_my_account(
    db: Session = Depends(get_db),
    username: str = Form(...),
    avater: Optional[UploadFile] = File(None),
    user: schemas.User = Depends(current_user)
):
    curr = get_user(db, user.id)
    curr.username = username
    if avater:
        curr.avater_url = await upload_image(avater)
    db.flush()
    db.commit()


async def upload_image(file):
    ext = os.path.splitext(file.filename)[1]
    fp = f'/images/{secrets.token_hex(24)}{ext}'
    async with aiofiles.open(fp, 'wb') as f:
        await f.write(await file.read())
    return (fastapi_config['openapi_prefix'] + fp).replace('//', '/')


@router.get('/me/posts', response_model=List[schemas.Post])
def my_posts(
    skip: int = Query(0),
    limit: int = Query(10),
    db: Session = Depends(get_db),
    user: schemas.User = Depends(current_user)
):
    return get_user_posts(db, user.id, skip, limit)


@router.get('/me/posts/{post_id}', response_model=List[schemas.Post])
def my_post(
    skip: int = Query(0),
    limit: int = Query(10),
    post_id: uuid.UUID = Path(...),
    db: Session = Depends(get_db),
    user: schemas.User = Depends(current_user)
):
    if (post := get_user_post(db, user.id, post_id)):
        return post
    else:
        raise exceptions.PostNotFoundException()


@router.delete('/me/posts/{post_id}', status_code=204)
def delete_my_post(
    post_id: uuid.UUID = Path(...),
    db: Session = Depends(get_db),
    user: schemas.User = Depends(current_user)
):
    if (post := get_user_post(db, user.id, post_id)):
        if post.owner_id != user.id:  # pragma: no cover
            raise exceptions.ForbiddenAccessException()
        db.query(models.Post).filter(
            models.Post.id == post_id).delete()
        db.flush()
        db.commit()
    else:
        raise exceptions.PostNotFoundException()


@router.get('/', response_model=List[schemas.User])
async def user_list(
    skip: int = Query(0),
    limit: int = Query(10),
    db: Session = Depends(get_db),
    user: schemas.User = Depends(current_user)
):
    return get_users(db, skip, limit)


@router.get('/{user_id}', response_model=schemas.User)
async def user(
    user_id: uuid.UUID = Path(...),
    db: Session = Depends(get_db),
    user: schemas.User = Depends(current_user)
):
    if (someuser := get_user(db, user_id)):
        return someuser
    else:
        raise exceptions.UserNotFoundException()


@router.get('/{user_id}/posts', response_model=List[schemas.Post])
async def user_posts(
    user_id: uuid.UUID = Path(...),
    skip: int = Query(0),
    limit: int = Query(10),
    db: Session = Depends(get_db),
    user: schemas.User = Depends(current_user)
):
    if (posts := get_user_posts(db, user_id, skip, limit)):
        return posts
    else:
        raise exceptions.UserNotFoundException()


@router.get('/{user_id}/posts/{post_id}', response_model=schemas.Post)
async def user_post(
    user_id: uuid.UUID = Path(...),
    post_id: uuid.UUID = Path(...),
    db: Session = Depends(get_db),
    user: schemas.User = Depends(current_user)
):
    if (post := get_user_post(db, user_id, post_id)):
        return post
    else:
        raise exceptions.UserNotFoundException()
