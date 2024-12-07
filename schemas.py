from pydantic import BaseModel
from typing import Optional

# Schema for creating users
class UserCreate(BaseModel):
    username: str
    password: str

    class Config:
        from_attributes = True  # Allow pydantic to handle SQLAlchemy models

# Schema for creating coaches
class CoachCreate(UserCreate):
    email: str
    location: str

    class Config:
        from_attributes = True

# Coach schema (Response schema)
class Coach(BaseModel):
    id: int
    username: str
    location: str
    email: str
    role: str

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str

# Base schema for a schedule
class ScheduleBase(BaseModel):
    exercises: str
    exercises_details: str
    cost_per_hour: float

    class Config:
        from_attributes = True

# Schedule schema for creating a new schedule
class ScheduleCreate(ScheduleBase):
    coach_id: int

    class Config:
        from_attributes = True

# Schedule schema for response (after creation)
class Schedule(ScheduleBase):
    id: int
    coach_id: int

    class Config:
        from_attributes = True
