from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app.core import config

engine = create_engine(
    config.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    connect_args=config.SQLALCHEMY_CONNECT_ARGS
)

SessionScope = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
# SessionScope = SessionScoping()
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
