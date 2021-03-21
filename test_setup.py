import os
from sqlalchemy import String, create_engine
from sqlalchemy import Table, Column, Integer
from sqlalchemy.dialects.postgresql import OID
from sqlalchemy.ext.declarative import declarative_base


url = (
    f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@"
    f"localhost:5432/{os.getenv('POSTGRES_DB')}"
)
Base = declarative_base()
engine = create_engine(url, echo=True)
Table(
    "attachment",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("oid", OID),
    Column("category", String(255), unique=True, default="Строки"),
    Column("content_type", String(255), nullable=True),
)
Base.metadata.create_all(engine, checkfirst=True)
