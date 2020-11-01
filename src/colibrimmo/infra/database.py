import logging

from contextlib import contextmanager
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.schema import CreateSchema


Base = declarative_base()


def create_postgres_namespace(engine: Engine, env_name: str):
    if not engine.dialect.has_schema(engine, env_name):
        engine.execute(CreateSchema(env_name))

@contextmanager
def session_scope(conn, database):
    """Provide a transactional scope around a series of operations."""
    engine = create_engine(conn+f'/{database}', echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logging.error(f'The following error during commit : {e}')
        raise
    finally:
        session.close()