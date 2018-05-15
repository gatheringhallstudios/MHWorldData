import os

import sqlalchemy
import sqlalchemy.orm
from contextlib import contextmanager

from .mappings import Base

def recreate_database(output_filename):
    "Recreates the database file, returning a session manager"
    if os.path.exists(output_filename):
        os.remove(output_filename)
   
    dbpath = f'sqlite:///{output_filename}'
    engine = sqlalchemy.create_engine(dbpath, echo=False)
    Base.metadata.create_all(engine)

    return sqlalchemy.orm.sessionmaker(bind=engine)

# adapted from sqlalchemy docs
@contextmanager
def session_scope(sessionmaker):
    """Provide a transactional scope around a series of operations."""
    session = sessionmaker()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
