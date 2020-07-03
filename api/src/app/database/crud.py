from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Dict, Union, Any, Tuple
from datetime import datetime, timedelta
from fastapi import Form, Header

import uuid
import os
import enum
import jwt

from app.database import models, schemas
from app.database.base import get_db
from app import exceptions
from passlib.context import CryptContext

pwd_context = CryptContext(["bcrypt"], deprecated="auto")


def hash_token(token):
    return pwd_context.hash(token)


def verify_token(token, hashed_token):
    return pwd_context.verify(token, hashed_token)


class TokenStatus(enum.IntEnum):
    VALID = enum.auto()
    INVALID = enum.auto()
    EXPIRED = enum.auto()


def get_user(db: Session, user_id: uuid.UUID) -> schemas.User:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_social_id(db: Session, social_id: int) -> schemas.User:
    return db.query(models.User).join(models.Token).filter(models.Token.social_id == social_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 10) -> List[schemas.User]:
    return db.query(models.User).offset(skip).limit(limit).all()


def create_post(db: Session, user: schemas.User, post: schemas.PostCreate):
    db_post = models.Post(title=post.title, description=post.description,
                          main=post.main, owner_id=user.id, stdout=post.stdout,
                          stderr=post.stderr, exitcode=post.exitcode)
    db.add(db_post)
    db.flush()
    db.commit()
    db.refresh(db_post)
    for img in post.posted_images:
        db_image = models.PostedImage(url=img, post_id=db_post.id)
        db.add(db_image)
        db.flush()
        db.commit()
        db.refresh(db_image)
    for img in post.generated_images:
        db_image = models.GeneratedImage(url=img, post_id=db_post.id)
        db.add(db_image)
        db.flush()
        db.commit()
        db.refresh(db_image)
    return db_post


def create_user(db: Session, user: schemas.UserCreate) -> schemas.User:  # pragma: no cover
    db_user = models.User(username=user.username, avater_url=user.avater_url)
    db.add(db_user)
    db.flush()
    db.commit()
    db.refresh(db_user)
    return db_user


def get_all_posts(db: Session, skip: int = 0, limit: int = 10) -> List[schemas.Post]:
    return db.query(models.Post).join(models.User).order_by(desc(models.Post.post_at)).offset(skip).limit(limit).all()


def fetch_new_posts(db: Session, post_at: str, skip: int = 0, limit: int = 1000) -> List[schemas.Post]:
    return db.query(models.Post).join(models.User).filter(models.Post.post_at > datetime.strptime(post_at, "%Y-%m-%dT%H:%M:%S.%f")).order_by(desc(models.Post.post_at)).offset(skip).limit(limit).all()


def fetch_old_posts(db: Session, post_at: str, skip: int = 0, limit: int = 10) -> List[schemas.Post]:
    return db.query(models.Post).filter(models.Post.post_at < datetime.strptime(post_at, "%Y-%m-%dT%H:%M:%S.%f")).join(models.User).order_by(desc(models.Post.post_at)).offset(skip).limit(limit).all()


def get_user_posts(db: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 10) -> List[schemas.Post]:
    return db.query(models.Post).join(models.User).filter(models.User.id == user_id).order_by(desc(models.Post.post_at)).offset(skip).limit(limit).all()


def get_user_post(db: Session, user_id: uuid.UUID, post_id: uuid.UUID) -> schemas.Post:
    return db.query(models.Post).join(models.User).filter(models.User.id == user_id, models.Post.id == post_id).first()


def create_token(db: Session, token: schemas.TokenCreate, owner_id: uuid.UUID) -> schemas.Token:  # pragma: no cover
    db_token = models.Token(
        social_id=token.social_id,
        refresh_token=hash_token(token.refresh_token),
        access_token_expire_at=datetime.utcnow() + timedelta(minutes=int(
            os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'])),
        refresh_token_expire_at=datetime.utcnow() + timedelta(minutes=int(
            os.environ['REFRESH_TOKEN_EXPIRE_MINUTES'])),
        owner_id=owner_id
    )
    db.add(db_token)
    db.flush()
    db.commit()
    db.refresh(db_token)
    return db_token


def update_token(db: Session, db_user: models.User, refresh_token) -> schemas.Token:
    db_token = db.query(models.Token).join(models.User).filter(
        models.User.id == db_user.id).first()
    db_token.refresh_token = hash_token(refresh_token)
    db_token.access_token_expire_at = datetime.utcnow() + timedelta(minutes=int(
        os.environ['ACCESS_TOKEN_EXPIRE_MINUTES']))
    db_token.refresh_token_expire_at = datetime.utcnow() + timedelta(minutes=int(
        os.environ['REFRESH_TOKEN_EXPIRE_MINUTES']))
    print('1', db_token.refresh_token, db_token.access_token_expire_at,
          db_token.refresh_token_expire_at)
    db.flush()
    db.commit()
    print('2', db_token.refresh_token, refresh_token)
    db_token = db.query(models.Token).join(models.User).filter(
        models.User.id == models.Token.owner_id).first()
    print('3', db_token.refresh_token, refresh_token)


def verify_access_token(db: Session, access_token) -> Tuple[TokenStatus, Union[Dict[str, Any], None]]:
    try:
        data = jwt.decode(
            access_token, key=os.environ['SECRET_KEY'], algorithms=[
                os.environ['AUTH_ALGORITHM']]
        )
    except jwt.ExpiredSignatureError:  # pragma: no cover
        data = jwt.decode(
            access_token, key=os.environ['SECRET_KEY'], algorithms=[
                os.environ['AUTH_ALGORITHM']], verify=False
        )
        user_id = data['sub']
        token: models.Token = db.query(models.Token).filter(
            models.Token.social_id == user_id).first()
        return TokenStatus.EXPIRED, None
    except:
        return TokenStatus.INVALID, None
    return TokenStatus.VALID, data


def verify_refresh_token(db: Session, access_token, refresh_token) -> Tuple[TokenStatus, Union[Dict[str, Any], None]]:
    try:
        data = jwt.decode(
            access_token, key=os.environ['SECRET_KEY'], algorithms=[
                os.environ['AUTH_ALGORITHM']]
        )
    except jwt.ExpiredSignatureError:  # pragma: no cover
        data = jwt.decode(
            access_token, key=os.environ['SECRET_KEY'], algorithms=[
                os.environ['AUTH_ALGORITHM']], verify=False
        )
    except:
        return TokenStatus.INVALID, None
    user_id = data['sub']
    token: models.Token = db.query(models.Token).filter(
        models.Token.social_id == user_id).first()
    print(refresh_token, token.refresh_token)
    if not verify_token(refresh_token, token.refresh_token):
        return TokenStatus.INVALID, None
    now = datetime.utcnow()
    if token.refresh_token_expire_at < now:  # pragma: no cover
        return TokenStatus.EXPIRED, None
    return TokenStatus.VALID, data


def current_user(access_token: str = Header(...)) -> models.User:
    db = next(get_db())
    status, data = verify_access_token(db, access_token)
    if status == TokenStatus.VALID and data:
        return get_user_by_social_id(db, data['sub'])
    elif status == TokenStatus.INVALID:
        raise exceptions.InvalidTokenException()
    elif status == TokenStatus.EXPIRED:  # pragma: no cover
        raise exceptions.ExpiredTokenException()
