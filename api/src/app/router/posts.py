from starlette.requests import Request
from fastapi import APIRouter, HTTPException, Depends, Body, Form, Query, Cookie, Path, WebSocket, Header
from aiohttp import ClientSession
from datetime import timedelta
from sqlalchemy.orm import Session
from typing import List
from app import exceptions
from app.database.crud import (
    current_user,
    get_all_posts,
    create_post,
    get_user_posts,
    fetch_new_posts,
    fetch_old_posts
)
from app.database.base import get_db
from app.database import schemas, models
from app.auth.oauth import oauth, authenticate_user, create_access_token
import os
import uuid
import asyncio


router = APIRouter()


@router.get('/', response_model=List[schemas.Post])
def get_rescent_posts(
    skip: int = Query(0),
    limit: int = Query(10),
    db: Session = Depends(get_db),
    user: schemas.User = Depends(current_user)
):
    return get_all_posts(db, skip, limit)


@router.get('/fetch', include_in_schema=False, response_model=List[schemas.Post])
def fetch_posts(
    post_at: str = Header(...),
    skip: int = Query(0),
    limit: int = Query(1000),
    db: Session = Depends(get_db)
):
    posts = fetch_new_posts(db, post_at, skip, limit)
    return posts


@router.get('/history', include_in_schema=False, response_model=List[schemas.Post])
def old_posts(
    post_at: str = Header(...),
    skip: int = Query(0),
    limit: int = Query(1000),
    db: Session = Depends(get_db)
):
    posts = fetch_old_posts(db, post_at, skip, limit)
    return posts


@router.post('/', status_code=204)
def new_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(current_user)
):
    create_post(db, user, post)
