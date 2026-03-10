"""
Seed mock city data for the Planning Service.
Creates 3-5 neighbourhoods, 50-100 houses, and collection rules for all waste types.
"""

import random
from datetime import date

from sqlalchemy.orm import Session

from .database import (
    Base,
    engine,
    SessionLocal,
    NeighbourhoodModel,
    HouseModel,
    CollectionRuleModel,
)

# Mock neighbourhood names
NEIGHBOURHOOD_NAMES = [
    "Downtown Core",
    "Riverside Heights",
    "North Park",
    "Westfield",
    "Lakeside",
]

# Street name components for generating addresses
STREET_PREFIXES = ["Oak", "Maple", "Cedar", "Pine", "Elm", "Birch", "Willow", "Spruce"]
STREET_SUFFIXES = ["Street", "Avenue", "Drive", "Lane", "Boulevard", "Way", "Road", "Court"]


def seed_neighbourhoods(db: Session, count: int = 5) -> list[NeighbourhoodModel]:
    """Create neighbourhoods."""
    created = []
    for i, name in enumerate(NEIGHBOURHOOD_NAMES[:count]):
        n = NeighbourhoodModel(name=name)
        db.add(n)
        db.flush()
        created.append(n)
    return created


def seed_houses(db: Session, neighbourhood_ids: list[int], total: int = 80) -> list[HouseModel]:
    """Create houses distributed across neighbourhoods. Total between 50-100."""
    houses = []
    house_id = 1
    for _ in range(total):
        nid = random.choice(neighbourhood_ids)
        street = f"{random.choice(STREET_PREFIXES)} {random.choice(STREET_SUFFIXES)}"
        number = random.randint(1, 999)
        address = f"{number} {street}"
        residents = random.randint(1, 6)
        # Each house has at least garbage; some have recycling and/or organics
        bin_types = ["garbage"]
        if random.random() < 0.85:
            bin_types.append("recycling")
        if random.random() < 0.7:
            bin_types.append("organics")
        h = HouseModel(
            address=address,
            neighbourhood_id=nid,
            estimated_residents=residents,
            bin_types_supported=bin_types,
        )
        db.add(h)
        db.flush()
        houses.append(h)
        house_id += 1
    return houses


def seed_collection_rules(db: Session) -> list[CollectionRuleModel]:
    """
    Collection rules: weekdays only, 7 AM - 5 PM.
    - garbage: Monday, Wednesday
    - recycling: Tuesday, Thursday
    - organics: Friday
    """
    rules = [
        CollectionRuleModel(waste_type="garbage", assigned_day=0, frequency="weekly", allowed_time_start="07:00", allowed_time_end="17:00"),
        CollectionRuleModel(waste_type="garbage", assigned_day=2, frequency="weekly", allowed_time_start="07:00", allowed_time_end="17:00"),
        CollectionRuleModel(waste_type="recycling", assigned_day=1, frequency="weekly", allowed_time_start="07:00", allowed_time_end="17:00"),
        CollectionRuleModel(waste_type="recycling", assigned_day=3, frequency="weekly", allowed_time_start="07:00", allowed_time_end="17:00"),
        CollectionRuleModel(waste_type="organics", assigned_day=4, frequency="weekly", allowed_time_start="07:00", allowed_time_end="17:00"),
    ]
    for r in rules:
        db.add(r)
    return rules


def run_seed():
    """Run full seed: create tables, then seed neighbourhoods, houses, and rules."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Skip if already seeded
        if db.query(NeighbourhoodModel).first():
            return
        neighbourhoods = seed_neighbourhoods(db, count=5)
        n_ids = [n.id for n in neighbourhoods]
        seed_houses(db, n_ids, total=80)
        seed_collection_rules(db)
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
