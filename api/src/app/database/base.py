from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from os import environ

if environ['NODE_ENV'] == 'development':
    engine = create_engine(
        environ['DB_URL'],
        connect_args={"check_same_thread": False}
    )
else:  # pragma: no cover
    engine = create_engine(
        environ['DB_URL'],
    )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
