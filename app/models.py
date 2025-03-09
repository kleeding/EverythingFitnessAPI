from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    private = Column(Boolean, server_default="False", nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    owner = relationship("User")


class Weight(Base):
    __tablename__ = "weights"

    id = Column(Integer, primary_key=True, nullable=False)
    datapoint = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    owner = relationship("User")


class Calorie(Base):
    __tablename__ = "calories"

    id = Column(Integer, primary_key=True, nullable=False)
    datapoint = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    owner = relationship("User")


class Step(Base):
    __tablename__ = "steps"

    id = Column(Integer, primary_key=True, nullable=False)
    datapoint = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    owner = relationship("User")


class Exercise(Base):
    __tablename__ = "exercise"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    weight = Column(Float, nullable=False)
    reps = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    owner = relationship("User")
