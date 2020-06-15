from starlette.requests import Request
from fastapi import APIRouter, HTTPException, Depends, Body, Form, Query, Cookie, Path
from aiohttp import ClientSession
from datetime import timedelta
from sqlalchemy.orm import Session
from typing import List
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
    login_required,
    get_users,
    get_user,
    get_user_posts,
    get_user_post
)
from app.database.base import get_db
from app.database import schemas, models
from app.auth.oauth import oauth, authenticate_user, create_access_token
import os
import uuid

router = APIRouter()


@router.get('/me', response_model=schemas.User)
async def my_account(
    db: Session = Depends(get_db),
    user: schemas.User = Depends(current_user)
):
    return get_user(db, user.id)


@router.put('/me', status_code=204)
async def update_my_account(
    db: Session = Depends(get_db),
    config: schemas.UserUpdate = Body(None),
    user: schemas.User = Depends(current_user)
):
    curr = get_user(db, user.id)
    if config.username:
        curr.username = config.username
    if config.avater_url:
        curr.avater_url = config.avater_url
    db.commit()


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
    skip: int = Query(0),
    limit: int = Query(10),
    post_id: uuid.UUID = Path(...),
    db: Session = Depends(get_db),
    user: schemas.User = Depends(current_user)
):
    if (post := get_user_post(db, user.id, post_id)):
        if post.owner_id != user.id:  # pragma: no cover
            raise exceptions.ForbiddenAccessException()
        db.query(models.Post).filter(
            models.Post.id == post_id).delete()
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
