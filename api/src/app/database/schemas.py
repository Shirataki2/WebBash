from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid


class PostBase(BaseModel):
    title: str
    description: str
    owner_id: uuid.UUID
    main: str


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: uuid.UUID
    upvotes: List[uuid.UUID] = []
    downvotes: List[uuid.UUID] = []

    class Config:
        orm_mode = True


class TokenBase(BaseModel):
    pass


class TokenCreate(TokenBase):
    social_id: int
    refresh_token: str


class Token(TokenBase):
    owner_id: uuid.UUID

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    pass


class UserCreate(UserBase):
    username: str
    avater_url: str


class UserUpdate(UserBase):
    username: Optional[str]
    avater_url: Optional[str]


class User(UserBase):
    id: uuid.UUID
    username: str
    avater_url: str
    banned: bool = False
    posts: List[uuid.UUID]
    upvoted_posts: List[uuid.UUID]
    downvoted_posts: List[uuid.UUID]

    class Config:
        orm_mode = True
