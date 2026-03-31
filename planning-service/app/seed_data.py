#Mock city data for the Planning Service
#Creates neighbourhoods, houses, and collection rules

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

NEIGHBOURHOOD_STREETS = {
    "The Annex": [
        "Bloor Street West",
        "Bathurst Street",
        "Spadina Road",
        "Bedford Road",
        "Brunswick Avenue",
    ],
    "Kensington Market": [
        "Augusta Avenue",
        "Baldwin Street",
        "Kensington Avenue",
        "St Andrew Street",
        "College Street",
    ],
    "Leslieville": [
        "Queen Street East",
        "Carlaw Avenue",
        "Jones Avenue",
        "Leslie Street",
        "Coxwell Avenue",
    ],
    "Cabbagetown": [
        "Parliament Street",
        "Carlton Street",
        "Wellesley Street East",
        "Sackville Street",
        "Sumach Street",
    ],
    "Yorkville": [
        "Yonge Street",
        "Davenport Road",
        "Cumberland Street",
        "Bay Street",
        "Avenue Road",
    ],
}


def seed_neighbourhoods(db: Session) -> list[NeighbourhoodModel]:
    #create one neighbourhood row per key in NEIGHBOURHOOD_STREETS
    created = []
    for name in NEIGHBOURHOOD_STREETS:
        n = NeighbourhoodModel(name=name)
        db.add(n)
        db.flush()
        created.append(n)
    return created


def seed_houses(db: Session, neighbourhoods: list[NeighbourhoodModel], total: int = 80) -> list[HouseModel]:
    #create houses where each address uses a street from that neighbourhoods list
    houses = []
    for _ in range(total):
        n = random.choice(neighbourhoods)
        street = random.choice(NEIGHBOURHOOD_STREETS[n.name])
        number = random.randint(1, 999)
        address = f"{number} {street}"
        residents = random.randint(1, 6)
        bin_types = ["garbage"]
        if random.random() < 0.85:
            bin_types.append("recycling")
        if random.random() < 0.7:
            bin_types.append("organics")
        h = HouseModel(
            address=address,
            neighbourhood_id=n.id,
            estimated_residents=residents,
            bin_types_supported=bin_types,
        )
        db.add(h)
        db.flush()
        houses.append(h)
    return houses


def seed_collection_rules(db: Session) -> list[CollectionRuleModel]:
    #collection rules: weekdays only, 7am to 5pm.
    #garbage: Monday, Wednesday
    #recycling: Tuesday, Thursday
    #organics: Friday

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
    #run seed to create tables, then seed neighbourhoods, houses, and rules
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(NeighbourhoodModel).first():
            return
        neighbourhoods = seed_neighbourhoods(db)
        seed_houses(db, neighbourhoods, total=80)
        seed_collection_rules(db)
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
