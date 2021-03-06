import os
from copy import copy

from sqlalchemy import create_engine, event
from sqlalchemy import Column, Integer, String
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, object_session
from sqlalchemy.dialects.postgresql import OID


class CustomOrm:
    db = {
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST"),
    }
    Base = declarative_base()
    session_factory = sessionmaker()

    def __init__(self):
        self.engine = create_engine(
            f'postgresql+psycopg2://{self.db["USER"]}:{self.db["PASSWORD"]}@'
            f'{self.db["HOST"]}:5432'
            f'/{self.db["NAME"]}',
            echo=True,
        )
        self.Base.metadata.create_all(self.engine, checkfirst=True)
        self.session_factory.configure(bind=self.engine)
        self.Session = scoped_session(self.session_factory)

    class Data(Base):
        __tablename__ = "attachment"
        id = Column(Integer, primary_key=True)
        oid = Column(OID)
        category = Column(String(255), unique=True, default="Строки")
        content_type = Column(String(255), nullable=True)

    @event.listens_for(Data, "after_delete")
    def remove_large_object_after_delete(_, connection, target):
        raw_connection = connection.connection
        l_obj = raw_connection.lobject(target.oid, "n")
        l_obj.unlink()
        raw_connection.commit()

    @event.listens_for(Data, "before_insert")
    def add_large_object_before_insert(_, connection, target):
        raw_connection = connection.connection
        l_obj = raw_connection.lobject(0, "wb", 0)
        target.oid = l_obj.oid
        l_obj.write(target.ldata)
        raw_connection.commit()

    @event.listens_for(Data, "load")
    def inject_large_object_after_load(target, _):
        session = object_session(target)
        conn = session.get_bind().raw_connection()
        l_obj = conn.lobject(target.oid, "rb")
        target.ldata = l_obj.read()

    def get_data_by_id_and_delete(self, data_id):
        session = self.Session()
        data = session.query(self.Data).get(data_id)
        if data:
            ldata_copy, content_type_copy = copy(data.ldata), copy(data.content_type)
            session.delete(data)
            session.commit()
            return [ldata_copy, content_type_copy]
        return None

    def create_data(self, data, category, content_type):
        session = self.Session()
        _data = self.Data()
        _data.ldata = data
        _data.category = category
        _data.content_type = content_type
        try:
            session.add(_data)
            session.commit()
            return _data
        except SQLAlchemyError:
            return None

    def get_categories_list(self):
        session = self.Session()
        _categories = (
            session.query().with_entities(self.Data.id, self.Data.category).all()
        )
        return [{"id": c[0], "name": c[1]} for c in _categories]

    def get_category_file(self, category_id):
        session = self.Session()
        _category_data = session.query(self.Data).filter(self.Data.id == category_id)
        return [{"id": _category_data[0].id, "name": "Скачать"}]
