import enum

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Column, String, DateTime, ForeignKey, BIGINT, UniqueConstraint, Integer, SmallInteger
from sqlalchemy.dialects.postgresql import JSONB, ENUM
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression
from sqlalchemy.sql.ddl import CreateColumn

from dataset_image_annotator.db import Base


class UTCNow(expression.FunctionElement):
    type = DateTime()


@compiles(UTCNow, 'postgresql')
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


@compiles(CreateColumn, 'postgresql')
def use_identity(element, compiler, **kw):
    result = compiler.visit_create_column(element, **kw).replace('SERIAL', 'INT GENERATED BY DEFAULT AS IDENTITY')

    return result.replace('BIGSERIAL', 'BIGINT GENERATED BY DEFAULT AS IDENTITY')


class BaseDBModel:
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, onupdate=UTCNow())


class UserGroup(BaseDBModel, Base):
    __tablename__ = 'user_groups'

    name = Column(String, nullable=False)


class User(SQLAlchemyBaseUserTableUUID, Base):
    group_id = Column(Integer, ForeignKey('user_groups.id'), nullable=True)


class ImageSample(BaseDBModel, Base):
    __tablename__ = 'image_samples'

    filename = Column(String, nullable=False)
    checksum = Column(String, nullable=False)
    location = Column(String, nullable=False, unique=True)


class AnnotationKeyEnum(enum.Enum):
    type = 'type'
    make = 'make'
    model = 'model'
    body = 'body'
    color = 'color'


class ImageSampleAnnotation(BaseDBModel, Base):
    __tablename__ = 'image_sample_annotations'

    image_sample_id = Column(Integer, ForeignKey('image_samples.id'), nullable=False)
    key = Column(ENUM(AnnotationKeyEnum, name='enum_image_sample_annotation_key'), nullable=False)
    value = Column(String, nullable=False)
    votes = Column(Integer, nullable=False, default=0)
    user_id = Column(Integer, ForeignKey('image_samples.id'), nullable=False)

    __table_args__ = (
        UniqueConstraint('image_sample_id', 'key', 'user_id', name='uq_image_sample_annotation_item'),
    )


class AnnotationVote(BaseDBModel, Base):
    __tablename__ = 'annotation_votes'

    annotation_id = Column(Integer, ForeignKey('image_sample_annotations.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('image_samples.id'), nullable=False)
    value = Column(SmallInteger, nullable=False, default=0)
