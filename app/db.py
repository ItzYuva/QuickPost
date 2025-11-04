'''
from collections.abc import AsyncGenerator
import uuid

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime
from fastapi_users.db import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTableUUID
from fastapi import Depends

DATABASE_URL = "sqlite+aiosqlite:///./test.db"


class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    posts = relationship("Post", back_populates="user")


class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    caption = Column(Text)
    url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="posts")


engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
'''

# app/db.py
from collections.abc import AsyncGenerator
import uuid
from datetime import datetime
import os

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from fastapi_users.db import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTableUUID
from fastapi import Depends

# Read DATABASE_URL from env
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

# Detect if we're running with Postgres
IS_POSTGRES = DATABASE_URL.startswith("postgres") or DATABASE_URL.startswith("postgresql")

# Import Postgres UUID type only if needed
if IS_POSTGRES:
    from sqlalchemy.dialects.postgresql import UUID as PG_UUID
    ID_TYPE = PG_UUID(as_uuid=True)
else:
    ID_TYPE = String

class Base(DeclarativeBase):
    pass

# Keep using fastapi-users' base user table (uses UUID-like id)
class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "user"
    posts = relationship("Post", back_populates="user")

class Post(Base):
    __tablename__ = "posts"

    # Primary key type depends on backend
    if IS_POSTGRES:
        id = Column(ID_TYPE, primary_key=True, default=uuid.uuid4)
    else:
        id = Column(ID_TYPE, primary_key=True, default=lambda: str(uuid.uuid4()))

    # user_id must match user's id type (UUID on Postgres, String on SQLite)
    if IS_POSTGRES:
        user_id = Column(ID_TYPE, ForeignKey("user.id"), nullable=False)
    else:
        user_id = Column(ID_TYPE, ForeignKey("user.id"), nullable=False)

    caption = Column(Text)
    url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="posts")

# engine & async session maker
engine = create_async_engine(DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
