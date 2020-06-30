from typing import Dict, Any

from sqlalchemy.ext.declarative import as_declarative, declared_attr

from sqlalchemy_mixins import AllFeaturesMixin

from app.db.session import SessionScope


class ModelExistError(ValueError):
    pass


@as_declarative()
class Base(object):
    id: Any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()


class BaseModel(Base, AllFeaturesMixin):
    __abstract__ = True

    @classmethod
    def all_by_page(cls, page: int = 1, limit: int = 20, **kwargs) -> Dict:
        start = (page - 1) * limit
        end = start + limit
        return cls.query.slice(start, end).all()

    @classmethod
    def get(cls, **kwargs) -> Dict:
        """Return the the first value in database based on given args.
        Example:
            User.get(id=5)
        """
        return cls.where(**kwargs).first()


BaseModel.set_session(SessionScope())
