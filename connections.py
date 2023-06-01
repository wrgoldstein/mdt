import os

from sqlalchemy import create_engine

name_to_env = {
    "dev": "env var here",
}

class ConnectionType(type):
    """
    A little big of syntactic sugar to make fetching connections nice.
    """
    def __getattr__(cls, key):
        # return create_engine(os.getenv(name_to_env.get(key)))
        return create_engine("postgresql://postgres:postgres@localhost:5432/mdt_dev")

class Connection(metaclass=ConnectionType):
    pass
