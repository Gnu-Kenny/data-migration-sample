from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum

from common.type.constants import YES, NO
from database import Base


class MigrationLog(Base):
    __tablename__ = "migration_log"

    id = Column(Integer, primary_key=True)
    reference_type = Column(String, doc="post(게시글), comment(댓글)")
    reference_id = Column(Integer, doc="post 또는 comment의 id")
    title = Column(String, default="")
    status = Column(Enum("READY", "RUN", "DONE"), default="READY", doc="진행 상태: 준비/진행중/완료")
    description = Column(Text, default="")
    result = Column(Enum("SUCCESS", "FAIL", ""), default="", doc="마이그레이션 성공 여부")
    err_msg = Column(Text, default="")
    created_at = Column(DateTime, nullable=False, default=datetime.now())


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String, default="익명")
    email = Column(String)
    password = Column(String)
    delete_yn = Column(Enum(YES, NO), default=NO)
    created_at = Column(DateTime, nullable=False, default=datetime.now())


class Post(Base):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    content = Column(Text)
    delete_yn = Column(Enum(YES, NO), default=NO)
    created_at = Column(DateTime, nullable=False, default=datetime.now())


class V1Comment(Base):
    __tablename__ = "v1comment"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    post_id = Column(Integer)
    parent_comment_id = Column(Integer)
    content = Column(Text)
    delete_yn = Column(Enum(YES, NO), default=NO)
    created_at = Column(DateTime, nullable=False, default=datetime.now())


class V2Comment(Base):
    __tablename__ = "v2comment"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    post_id = Column(Integer)
    parent_comment_id = Column(Integer)
    content = Column(Text)
    delete_yn = Column(Enum(YES, NO), default=NO)
    created_at = Column(DateTime, nullable=False, default=datetime.now())


class MappingComment(Base):
    __tablename__ = "mapping_comment"

    id = Column(Integer, primary_key=True)
    v1comment_id = Column(Integer)
    v2comment_id = Column(Integer)
    description = Column(Text, default="")
    created_by = Column(Text, nullable=False, doc="생성된 시점, ex) V1, V2")
    created_at = Column(DateTime, nullable=False, default=datetime.now())
