from pydantic import BaseModel, EmailStr, ConfigDict
from typing import List
from datetime import datetime, date


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int | None


# User schemas
class UserBase(BaseModel):
    username: str


class UserLogin(UserBase):
    password: str


class UserCreate(UserLogin):
    email: EmailStr


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int  # could remove this
    created_at: datetime


# Post schemas
class PostBase(BaseModel):
    title: str
    content: str
    private: bool = True


class Post(PostBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut


class PostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    Post: Post
    votes: int


# Data schemas
# This base data schema covers weight/calories/steps
class DataEntry(BaseModel):
    date: datetime
    datapoint: float


class DataOut(DataEntry):
    # id: int
    created_at: datetime
    # owner_id: int
    # owner: UserOut


# Exercise schemas - reqs a exercise name and reps
class ExerciseEntry(DataEntry):
    name: str
    reps: int


class ExerciseOut(ExerciseEntry):
    # id: int
    created_at: datetime
    owner_id: int
    owner: UserOut

    # class Config:
    #     from_attributes = True


class ExerciseBasic(ExerciseEntry):
    date: date
    datapoint: int | float


class AllData(BaseModel):
    weight_data: List[DataEntry] = []
    calories_data: List[DataEntry] = []
    steps_data: List[DataEntry] = []
    exercise_data: List[ExerciseBasic] = []


class Vote(BaseModel):
    post_id: int
    dir: int
