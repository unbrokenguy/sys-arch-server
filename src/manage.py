#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from sqlalchemy import String, create_engine
from sqlalchemy import Table, Column, Integer
from sqlalchemy.dialects.postgresql import OID
from sqlalchemy.ext.declarative import declarative_base

from server.settings import DATABASE_URL


def main():
    """Run administrative tasks."""
    url = DATABASE_URL
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
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
