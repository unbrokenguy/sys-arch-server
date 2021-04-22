from copy import copy

from sqlalchemy import create_engine, event
from sqlalchemy import Column, Integer, String
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, object_session
from sqlalchemy.dialects.postgresql import OID
from server.settings import DATABASE_URL

Base = declarative_base()


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


session_factory = sessionmaker()
url = DATABASE_URL
engine = create_engine(url, echo=True)
Base.metadata.create_all(engine, checkfirst=True)
session_factory.configure(bind=engine)
Session = scoped_session(session_factory)


class DataBase:

    @staticmethod
    def get_data_by_id_and_delete(data_id):
        session = Session()
        data = session.query(Data).get(data_id)
        if data:
            ldata_copy, content_type_copy = copy(data.ldata), copy(data.content_type)
            session.delete(data)
            session.commit()
            return [ldata_copy, content_type_copy]
        return None

    @staticmethod
    def create_data(data, category, content_type):
        session = Session()
        _data = Data()
        _data.ldata = data
        _data.category = category
        _data.content_type = content_type
        try:
            session.add(_data)
            session.commit()
            return _data
        except SQLAlchemyError as e:
            print(e)
            return None

    @staticmethod
    def get_categories_list():
        session = Session()
        _categories = (
            session.query().with_entities(Data.id, Data.category).all()
        )
        return [{"id": c[0], "name": c[1]} for c in _categories]

    @staticmethod
    def get_category_file(category_id):
        session = Session()
        try:
            _category_data = session.query(Data).filter(Data.id == category_id)
            return [{"id": _category_data[0].id, "name": "Скачать"}]
        except SQLAlchemyError:
            return None
          