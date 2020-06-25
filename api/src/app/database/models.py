from sqlalchemy import Boolean, Column, Table, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from sqlalchemy_utils import UUIDType

from app.database.base import Base
from datetime import datetime
import uuid


follow_table = Table('follows', Base.metadata,
                     Column('followee_id', UUIDType(binary=False),
                            ForeignKey('users.id')),
                     Column('follower_id', UUIDType(binary=False),
                            ForeignKey('users.id')),
                     )


class User(Base):
    __tablename__ = 'users'
    id = Column(UUIDType(binary=False), primary_key=True,
                default=uuid.uuid4, index=True, unique=True)
    username = Column(String(length=32), index=True)
    avater_url = Column(String(length=256))
    banned = Column(Boolean, default=False)

    posts = relationship("Post", back_populates="owner")
    token = relationship("Token", back_populates="owner")
    upvoted_posts = relationship(
        "Post", back_populates="upvotes")
    downvoted_posts = relationship(
        "Post", back_populates="downvotes")
    followee = relationship(
        "User",
        lambda: follow_table,
        primaryjoin=lambda: User.id == follow_table.c.follower_id,
        secondaryjoin=lambda: User.id == follow_table.c.followee_id,
        backref="follower"
    )


user_upvotes = Table('user_upvotes', Base.metadata,
                     Column('user_id', UUIDType(binary=False),
                            ForeignKey('users.id')),
                     Column('post_id', UUIDType(binary=False),
                            ForeignKey('posts.id')),
                     )

user_downvotes = Table('user_downvotes', Base.metadata,
                       Column('user_id', UUIDType(binary=False),
                              ForeignKey('users.id')),
                       Column('post_id', UUIDType(binary=False),
                              ForeignKey('posts.id')),
                       )


class Post(Base):
    __tablename__ = 'posts'
    id = Column(UUIDType(binary=False), primary_key=True,
                default=uuid.uuid4, index=True)
    title = Column(String(length=32))
    description = Column(String(length=280))
    main = Column(String(length=4000))
    post_at = Column(DateTime, default=datetime.now())
    owner_id = Column(UUIDType(binary=False), ForeignKey("users.id"))

    owner = relationship("User", back_populates="posts")
    upvotes = relationship(
        "User",
        secondary=user_upvotes,
        back_populates="upvoted_posts"
    )
    downvotes = relationship(
        "User",
        secondary=user_downvotes,
        back_populates="downvoted_posts"
    )


class Token(Base):
    __tablename__ = 'tokens'
    social_id = Column(Integer, primary_key=True, index=True, unique=True)
    refresh_token = Column(String)
    access_token_expire_at = Column(DateTime)
    refresh_token_expire_at = Column(DateTime)
    owner_id = Column(UUIDType(binary=False), ForeignKey('users.id'))

    owner = relationship("User", back_populates="token")
