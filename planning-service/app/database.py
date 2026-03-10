"""
Database setup for Planning Service.
Uses SQLite with SQLAlchemy async (optional) or sync for simplicity.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Date, ForeignKey, JSON
import os

# SQLite path - persist in project data directory
DATABASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATABASE_DIR, exist_ok=True)
DATABASE_URL = f"sqlite:///{os.path.join(DATABASE_DIR, 'planning.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- SQLAlchemy ORM models (DB schema) ---

class NeighbourhoodModel(Base):
    __tablename__ = "neighbourhoods"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)


class HouseModel(Base):
    __tablename__ = "houses"
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(255), nullable=False)
    neighbourhood_id = Column(Integer, ForeignKey("neighbourhoods.id"), nullable=False)
    estimated_residents = Column(Integer, default=1)
    bin_types_supported = Column(JSON)  # list of strings: ["garbage", "recycling", "organics"]


class CollectionRuleModel(Base):
    __tablename__ = "collection_rules"
    id = Column(Integer, primary_key=True, index=True)
    waste_type = Column(String(50), nullable=False)  # garbage, recycling, organics
    assigned_day = Column(Integer, nullable=False)  # 0-4
    frequency = Column(String(50), default="weekly")
    allowed_time_start = Column(String(10), default="07:00")
    allowed_time_end = Column(String(10), default="17:00")


class WeeklyScheduleModel(Base):
    __tablename__ = "weekly_schedule"
    id = Column(Integer, primary_key=True, index=True)
    neighbourhood_id = Column(Integer, ForeignKey("neighbourhoods.id"), nullable=False)
    waste_type = Column(String(50), nullable=False)
    scheduled_day = Column(Integer, nullable=False)
    week_start = Column(Date, nullable=False)  # which week this schedule applies to


class RouteModel(Base):
    __tablename__ = "routes"
    id = Column(Integer, primary_key=True, index=True)
    truck_id = Column(String(50), nullable=False)
    date = Column(Date, nullable=False)
    neighbourhood_id = Column(Integer, ForeignKey("neighbourhoods.id"), nullable=False)
    waste_type = Column(String(50), nullable=False)
    stops = Column(JSON, nullable=False)  # list of {house_id, address, order_index}


def get_db():
    """Dependency that yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)
