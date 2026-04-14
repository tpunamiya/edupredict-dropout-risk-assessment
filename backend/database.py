from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# SQLite database file (will be created automatically)
SQLALCHEMY_DATABASE_URL = "sqlite:///./edupredict.db"

# Create engine
# check_same_thread=False needed for SQLite to work with FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for database models
Base = declarative_base()

# Create engine
# check_same_thread=False needed for SQLite to work with FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# Create session factory 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # A sesssion

# Base class for database models
Base = declarative_base()

# Database model - defines the table strucutre 
class PredictionHistory(Base):
    """Table to store all predictions"""
    __tablename__ = "predictions"
    
    # Columns
    id = Column(Integer, primary_key=True, index=True)
    
    # Student information
    age = Column(Integer)
    gender = Column(String)
    attendance_rate = Column(Float)
    previous_grade = Column(String)
    distance_to_school = Column(Float)
    parent_education = Column(String)
    household_income = Column(String)
    
    # Prediction results
    risk_score = Column(Float)
    risk_category = Column(String)
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow) 

    # Create all tables in the database
Base.metadata.create_all(bind=engine)

# Dependency function for FastAPI
def get_db():
    """
    Creates a new database session for each request
    Automatically closes after the request is done
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()