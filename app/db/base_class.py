from typing import Dict

from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy_mixins import AllFeaturesMixin

from app.db.session import SessionScope


class ModelExistError(ValueError):
    pass


# TODO: add tests for serializer and move to BaseModel
class CustomBase(object):
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


Base = declarative_base(cls=CustomBase)


class BaseModel(Base, AllFeaturesMixin):
    __abstract__ = True

    # TODO: page > 1
    @classmethod
    def all_by_page(cls, page: int = 1, limit: int = 20, **kwargs) -> Dict:
        start = (page - 1) * limit
        end = start + limit
        # pytest.set_trace()
        return cls.query.slice(start, end).all()

    @classmethod
    def get(cls, **kwargs) -> Dict:
        """Return the the first value in database based on given args.
        Example:
            User.get(id=5)
        """
        return cls.where(**kwargs).first()


BaseModel.set_session(SessionScope())
