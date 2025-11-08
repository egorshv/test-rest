from __future__ import annotations

import pathlib
import sys

from sqlalchemy import select
from sqlalchemy.orm import Session

BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.db.session import SessionLocal
from app.models import Activity, Building, Organization, OrganizationPhone


def create_buildings(db: Session) -> dict[str, Building]:
    building_payload = [
        {"address": "г. Москва, ул. Ленина 1, офис 3", "latitude": 55.7522, "longitude": 37.6156},
        {"address": "г. Новосибирск, ул. Блюхера 32/1", "latitude": 55.0736, "longitude": 82.9590},
        {"address": "г. Санкт-Петербург, Невский пр. 12", "latitude": 59.9343, "longitude": 30.3351},
    ]
    mapping: dict[str, Building] = {}
    for payload in building_payload:
        building = db.scalar(select(Building).where(Building.address == payload["address"]))
        if not building:
            building = Building(**payload)
            db.add(building)
            db.flush()
        mapping[building.address] = building
    return mapping


def create_activities(db: Session) -> dict[str, Activity]:
    activity_payload = [
        {"name": "Еда", "parent": None},
        {"name": "Мясная продукция", "parent": "Еда"},
        {"name": "Молочная продукция", "parent": "Еда"},
        {"name": "Автомобили", "parent": None},
        {"name": "Грузовые", "parent": "Автомобили"},
        {"name": "Легковые", "parent": "Автомобили"},
        {"name": "Запчасти", "parent": "Легковые"},
        {"name": "Аксессуары", "parent": "Легковые"},
    ]
    activity_map: dict[str, Activity] = {}

    for payload in activity_payload:
        existing = db.scalar(select(Activity).where(Activity.name == payload["name"]))
        if existing:
            activity_map[existing.name] = existing
            continue

        if payload["parent"]:
            parent = activity_map.get(payload["parent"]) or db.scalar(
                select(Activity).where(Activity.name == payload["parent"])
            )
            if not parent:
                raise ValueError(f"Parent activity '{payload['parent']}' not found")
            level = parent.level + 1
        else:
            parent = None
            level = 1

        if level > 3:
            raise ValueError(f"Activity '{payload['name']}' exceeds 3 level depth")

        activity = Activity(name=payload["name"], parent=parent, level=level)
        db.add(activity)
        db.flush()
        activity_map[activity.name] = activity
    return activity_map


def create_organizations(db: Session, buildings: dict[str, Building], activities: dict[str, Activity]) -> None:
    organization_payload = [
        {
            "name": "ООО Рога и Копыта",
            "building": "г. Новосибирск, ул. Блюхера 32/1",
            "phones": ["2-222-222", "3-333-333", "+7-923-666-13-13"],
            "activities": ["Еда", "Мясная продукция"],
        },
        {
            "name": "ЗАО Сытный Дом",
            "building": "г. Москва, ул. Ленина 1, офис 3",
            "phones": ["+7-495-111-22-33"],
            "activities": ["Еда", "Молочная продукция"],
        },
        {
            "name": "ООО АвтоМакс",
            "building": "г. Санкт-Петербург, Невский пр. 12",
            "phones": ["+7-812-555-00-11"],
            "activities": ["Автомобили", "Легковые", "Аксессуары"],
        },
        {
            "name": "ИП ГрузЛайн",
            "building": "г. Москва, ул. Ленина 1, офис 3",
            "phones": ["+7-495-700-44-55"],
            "activities": ["Автомобили", "Грузовые"],
        },
    ]

    for payload in organization_payload:
        existing = db.scalar(select(Organization).where(Organization.name == payload["name"]))
        if existing:
            continue

        building = buildings[payload["building"]]
        organization = Organization(name=payload["name"], building=building)
        for activity_name in payload["activities"]:
            activity = activities.get(activity_name)
            if not activity:
                raise ValueError(f"Activity '{activity_name}' not found")
            organization.activities.append(activity)
        for phone in payload["phones"]:
            organization.phones.append(OrganizationPhone(phone_number=phone))
        db.add(organization)


def seed() -> None:
    db = SessionLocal()
    try:
        buildings = create_buildings(db)
        activities = create_activities(db)
        create_organizations(db, buildings, activities)
        db.commit()
        print("Database seeded successfully.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
