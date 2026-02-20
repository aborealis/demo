import os
from pydantic import BaseModel
from sqlmodel import create_engine


class DocStoreParams(BaseModel):
    table_name: str
    dimension: int


TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]

engine_tests = create_engine(
    TEST_DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
)
