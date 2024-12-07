from sqlalchemy import (
    create_engine, Column, Integer, String, ForeignKey, Float
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Base User model
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="admin")
    type = Column(String)  # Discriminator column (this column stores the type)

    # Remove schedules relationship from User and move it to Coach
    __mapper_args__ = {
        "polymorphic_identity": "user",  # Identity for the User model
        "polymorphic_on": type,          # Pointing to the 'type' column for polymorphism
    }

# Derived Coach model
class Coach(User):
    __tablename__ = "coaches"

    id = Column(Integer, ForeignKey("users.id"), primary_key=True)  # FK to users
    email = Column(String, unique=True, index=True)
    location = Column(String)

    # Define the schedules relationship on the Coach model instead
    schedules = relationship("Schedule", back_populates="coach")

    __mapper_args__ = {
        "polymorphic_identity": "coach",  # Identity for the Coach model
    }

class Schedule(Base):
    __tablename__ = 'schedules'

    id = Column(Integer, primary_key=True, index=True)
    coach_id = Column(Integer, ForeignKey('coaches.id'))  # ForeignKey referencing Coach
    exercises = Column(String)
    exercises_details = Column(String)
    cost_per_hour = Column(Float)

    # Define the relationship with the Coach
    coach = relationship("Coach", back_populates="schedules")

# Base.metadata.drop_all(bind=engine)
# Create tables
Base.metadata.create_all(bind=engine)
