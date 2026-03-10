"""
Database for Operations Service - stores pickup events only.
"""

import os
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATABASE_DIR, exist_ok=True)
DATABASE_URL = f"sqlite:///{os.path.join(DATABASE_DIR, 'operations.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class PickupEventModel(Base):
    __tablename__ = "pickup_events"
    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, nullable=False, index=True)
    house_id = Column(Integer, nullable=False)
    waste_type = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), nullable=False)  # completed, missed, delayed


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
