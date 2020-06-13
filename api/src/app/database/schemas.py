from typing import List
from pydantic import BaseModel
from datetime import datetime
import uuid


class PostBase(BaseModel):
    title: str
    description: str
    main: str


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    upvotes: List['User'] = []
    downvotes: List['User'] = []

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: uuid.UUID
    token: 'Token'
    banned: bool = False
    posts: List[Post] = []
    upvoted_posts: List[Post] = []
    downvoted_posts: List[Post] = []

    class Config:
        orm_mode = True


class TokenBase(BaseModel):
    pass


class TokenCreate(TokenBase):
    social_id: int
    social_name: str
    refresh_token: str


class Token(TokenCreate):
    owner_id: uuid.UUID
    access_token_expire_at: datetime
    refresh_token_expire_at: datetime

    class Config:
        orm_mode = True
