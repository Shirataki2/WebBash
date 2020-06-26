from typing import List, Optional, Any, ForwardRef
from pydantic import BaseModel
from datetime import datetime
import uuid


class PostBase(BaseModel):
    title: str
    description: str
    main: str
    stdout: str
    stderr: str
    exitcode: str
    posted_images: List[Any]
    generated_images: List[Any]


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    upvotes: List[uuid.UUID] = []
    downvotes: List[uuid.UUID] = []
    owner: "User"
    post_at: datetime

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

    class Config:
        orm_mode = True


Post.update_forward_refs()
