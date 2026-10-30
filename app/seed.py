
from sqlalchemy import select

from app.database import SessionLocal
from app.models import Campus, Building, Floor, Room, Equipment


def seed_database():
    with SessionLocal() as db:

        # Create sample campus
        campus = db.scalar(
            select(Campus).where(Campus.name == "WattWise Demo Campus")
        )

        if campus is None:
            campus = Campus(
                name="WattWise Demo Campus",
                location="Demo Location, Karnataka",
                timezone="Asia/Kolkata"
            )
            db.add(campus)
            db.flush()

        building_data = [
            ("Academic Block", "ACB"),
            ("Computer Lab", "CLB"),
            ("Library", "LIB"),
            ("Administration Block", "ADM"),
        ]

        for building_name, code in building_data:
            building = db.scalar(
                select(Building).where(
                    Building.campus_id == campus.id,
                    Building.name == building_name
                )
            )

            if building is None:
                building = Building(
                    campus_id=campus.id,
                    name=building_name,
                    building_code=code,
                    description="Sample demonstration building"
                )
                db.add(building)
                db.flush()

            # Create a ground floor if it doesn't exist
            floor = db.scalar(
                select(Floor).where(
                    Floor.building_id == building.id,
                    Floor.floor_number == 0
                )
            )

            if floor is None:
                floor = Floor(
                    building_id=building.id,
                    floor_number=0,
                    name="Ground Floor"
                )
                db.add(floor)
                db.flush()

            # Create a sample room
            room = db.scalar(
                select(Room).where(
                    Room.floor_id == floor.id,
                    Room.room_code == "ROOM-001"
                )
            )

            if room is None:
                room = Room(
                    floor_id=floor.id,
                    room_code="ROOM-001",
                    room_type="General"
                )
                db.add(room)
                db.flush()

            # Create sample equipment
            equipment_data = [
                ("AC-001", "Air Conditioner", "AC", 2.0),
                ("FAN-001", "Ceiling Fan", "FAN", 0.075),
                ("LIGHT-001", "LED Light", "LIGHT", 0.04),
            ]

            if code == "CLB":
                equipment_data.append(
                    ("PC-001", "Desktop Computer", "COMPUTER", 0.2)
                )

            for tag, name, equipment_type, power in equipment_data:
                existing = db.scalar(
                    select(Equipment).where(
                        Equipment.asset_tag == f"{code}-{tag}"
                    )
                )

                if existing is None:
                    db.add(
                        Equipment(
                            room_id=room.id,
                            asset_tag=f"{code}-{tag}",
                            name=name,
                            equipment_type=equipment_type,
                            rated_power_kw=power,
                            quantity=1
                        )
                    )

        db.commit()
        print("Sample campus data inserted successfully!")


if __name__ == "__main__":
    seed_database()
