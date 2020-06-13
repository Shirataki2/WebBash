from sqlalchemy.orm import Session
from typing import List, Dict, Union, Any, Tuple
from datetime import datetime, timedelta

import uuid
import os
import enum
import jwt

from app.database import models, schemas
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


def get_user(db: Session, user_id: uuid.UUID) -> models.User:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_social_id(db: Session, social_id: int) -> models.User:
    print(models.User.token)
    return db.query(models.User).join(models.Token).filter(models.Token.social_id == social_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_token(db: Session, token: schemas.TokenCreate, owner_id: uuid.UUID) -> models.Token:
    db_token = models.Token(
        social_id=token.social_id,
        social_name=token.social_name,
        refresh_token=token.refresh_token,
        access_token_expire_at=datetime.utcnow() + timedelta(minutes=int(
            os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'])),
        refresh_token_expire_at=datetime.utcnow() + timedelta(minutes=int(
            os.environ['REFRESH_TOKEN_EXPIRE_MINUTES'])),
        owner_id=owner_id
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token


def update_token(db: Session, db_user: models.User, refresh_token) -> models.Token:
    db_token = db.query(models.Token).join(models.User).filter(
        models.User.id == models.Token.owner_id).first()
    db_token.refresh_token = refresh_token
    db_token.access_token_expire_at = datetime.utcnow() + timedelta(minutes=int(
        os.environ['ACCESS_TOKEN_EXPIRE_MINUTES']))
    db_token.refresh_token_expire_at = datetime.utcnow() + timedelta(minutes=int(
        os.environ['REFRESH_TOKEN_EXPIRE_MINUTES']))
    db.commit()


def verify_access_token(db: Session, access_token) -> Tuple[TokenStatus, Union[Dict[str, Any], None]]:
    try:
        data = jwt.decode(
            access_token, key=os.environ['SECRET_KEY'], algorithms=[
                os.environ['AUTH_ALGORITHM']]
        )
    except jwt.ExpiredSignatureError:
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
    except jwt.ExpiredSignatureError:
        data = jwt.decode(
            access_token, key=os.environ['SECRET_KEY'], algorithms=[
                os.environ['AUTH_ALGORITHM']], verify=False
        )
    except:
        return TokenStatus.INVALID, None
    user_id = data['sub']
    token_: models.Token = db.query(models.Token).filter(
        models.Token.social_id == user_id).first()
    print(refresh_token, token_.refresh_token)
    if refresh_token != token_.refresh_token:
        return TokenStatus.INVALID, None
    now = datetime.utcnow()
    if token_.refresh_token_expire_at < now:
        return TokenStatus.EXPIRED, None
    return TokenStatus.VALID, data
