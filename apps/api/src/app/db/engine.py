from functools import lru_cache

from sqlalchemy import Engine, create_engine


@lru_cache(maxsize=8)
def get_engine(database_url: str) -> Engine:
    """One cached engine per database URL, shared across requests."""
    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    return create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)
