from copy import copy

from sqlalchemy import create_engine, event
from sqlalchemy import Column, Integer, String
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, object_session
from sqlalchemy.dialects.postgresql import OID
from server.settings import DATABASE_URL
from server.utils import SingletonMeta

Base = declarative_base()


class Data(Base):
    """
    SQLAlchemy model

    Attributes:
        id: Primary key.
        oid: Id of Postgres LOB (Large Object).
        category: LOB category string.
        content_type: MIMETYPE of LOB.
    """

    __tablename__ = "attachment"
    id = Column(Integer, primary_key=True)
    oid = Column(OID)
    category = Column(String(255), unique=True, default="Строки")
    name = Column(String(255), default="")
    content_type = Column(String(255), nullable=True)


@event.listens_for(Data, "after_delete")
def remove_large_object_after_delete(_, connection, target):
    """
    Delete LOB from Postgres.
    After delete event listener.
    Args:
        _: Meta
        connection: Connection to database.
        target: Deleted object.
    """
    raw_connection = connection.connection
    l_obj = raw_connection.lobject(target.oid, "n")
    l_obj.unlink()
    raw_connection.commit()


@event.listens_for(Data, "before_insert")
def add_large_object_before_insert(_, connection, target):
    """
    Creates LOB in Postgres and set target.oid = LOB.oid
    Before Insert event listener.
    Args:
        _: Meta
        connection: Connection to database.
        target: Created object.
    """
    raw_connection = connection.connection
    l_obj = raw_connection.lobject(0, "wb", 0)
    target.oid = l_obj.oid
    l_obj.write(target.ldata)
    raw_connection.commit()


@event.listens_for(Data, "load")
def inject_large_object_after_load(target, _):
    """
    Every Data object call. Add attribute ldata to object with LOB data.
    Args:
        target: Created object.
        _: kwargs.
    """
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


class DataBase(metaclass=SingletonMeta):
    """Singleton
    The DataBase class encapsulates methods for interacting with the sql database.
    Due to the fact that all methods are static,
    So no need to create more than one instance.
    Methods:
        get_data_by_id_and_delete: Retrieve data by id and delete it from database.
        create_data: Create data in database.
        get_categories_list: Retrieve list of Categories.
        get_category_file: Retrieve file by category id.
    """

    @staticmethod
    def get_data_by_id_and_delete(data_id):
        """
        Retrieve data by id and delete it from Postgres.
        Args:
            data_id: Primary key.
        Returns:
            if Data object with id == data_id exist returns obj.ldata and obj.content_type else None, None
        """
        session = Session()
        data = session.query(Data).get(data_id)
        if data:
            data_copy, content_type_copy = copy(data), copy(data.content_type)
            session.delete(data)
            session.commit()
            session.flush()
            return data_copy, content_type_copy
        return None, None

    @staticmethod
    def create_data(data, category, content_type, filename):
        """
        Creates Data in Postgres.
        Args:
            filename: Original file name.
            data: File or String to create in db.
            category: Data category string.
            content_type: MIMETYPE of Data.

        Returns:
            If Data object created return object.
            If Error occurred return None.
        """
        session = Session()
        _data = Data()
        _data.ldata = data
        _data.category = category
        _data.content_type = content_type
        _data.name = filename
        try:
            session.add(_data)
            session.commit()
            return _data
        except SQLAlchemyError:
            session.rollback()
            return None

    @staticmethod
    def get_categories_list():
        """
        Retrieve list of categories that exists in Postgres.
        Categories collection of all Data.category in Postgres.
        Category id == Data.id with this category.
        Category is unique value so on data one category.
        Returns:
            List of Categories.
        """
        session = Session()
        _categories = session.query().with_entities(Data.id, Data.category).all()
        session.flush()
        return _categories

    @staticmethod
    def get_category_file(category_id):
        """
        Retrieve list of Data in category.
        Args:
            category_id: Id of Category (Data.id)
        Returns:
            If Data object exist return List with object in json format
            If Error occurred return None.
        """
        session = Session()
        try:
            _category_data = session.query(Data).filter(Data.id == category_id)
            return _category_data.all()[0] if len(_category_data.all()) > 0 else None
        except SQLAlchemyError:
            session.rollback()
            return None
