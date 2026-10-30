
from datetime import datetime, timedelta
import math

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Building
from app.energy_models import (
    DataSource,
    EnergyReading,
    OccupancyReading,
    WeatherReading,
)


def seed_energy_data():
    with SessionLocal() as db:

        source = db.scalar(
            select(DataSource).where(
                DataSource.name == "WattWise Demo Simulator"
            )
        )

        if source is None:
            source = DataSource(
                name="WattWise Demo Simulator",
                source_type="SIMULATED",
                description="Synthetic demo data, not actual meter readings."
            )
            db.add(source)
            db.flush()

        # Remove previously generated readings before inserting again
        db.query(EnergyReading).filter(
            EnergyReading.data_source_id == source.id
        ).delete(synchronize_session=False)

        db.query(OccupancyReading).filter(
            OccupancyReading.data_source_id == source.id
        ).delete(synchronize_session=False)

        db.query(WeatherReading).filter(
            WeatherReading.data_source_id == source.id
        ).delete(synchronize_session=False)

        buildings = db.scalars(
            select(Building).order_by(Building.id)
        ).all()

        if not buildings:
            raise ValueError("No buildings found. Run python -m app.seed first.")

        peak_power = {
            "Academic Block": 12.0,
            "Computer Lab": 18.0,
            "Library": 10.0,
            "Administration Block": 7.0,
        }

        max_occupancy = {
            "Academic Block": 100,
            "Computer Lab": 60,
            "Library": 80,
            "Administration Block": 40,
        }

        start_time = datetime(2026, 10, 29, 0, 0)

        for interval in range(96):
            timestamp = start_time + timedelta(minutes=15 * interval)
            hour = timestamp.hour + timestamp.minute / 60

            temperature = 26 + 4 * math.sin(
                2 * math.pi * (hour - 6) / 24
            )

            humidity = 60 - 12 * math.sin(
                2 * math.pi * (hour - 6) / 24
            )

            db.add(
                WeatherReading(
                    data_source_id=source.id,
                    timestamp=timestamp,
                    temperature_c=round(temperature, 2),
                    humidity_percent=round(humidity, 2),
                    weather_location="Demo Campus"
                )
            )

            if 8 <= hour < 17:
                occupancy_factor = 0.85
                load_factor = 0.90
            elif 17 <= hour < 20:
                occupancy_factor = 0.30
                load_factor = 0.45
            else:
                occupancy_factor = 0.05
                load_factor = 0.22

            for building in buildings:
                peak = peak_power.get(building.name, 8.0)

                variation = 1 + 0.08 * math.sin(
                    2 * math.pi * hour / 24
                )

                power = peak * load_factor * variation
                energy = power * 0.25

                occupancy = int(
                    max_occupancy.get(building.name, 50)
                    * occupancy_factor
                )

                db.add(
                    EnergyReading(
                        building_id=building.id,
                        equipment_id=None,
                        data_source_id=source.id,
                        timestamp=timestamp,
                        interval_minutes=15,
                        power_kw=round(power, 4),
                        energy_kwh=round(energy, 4),
                        reading_status="VALID"
                    )
                )

                db.add(
                    OccupancyReading(
                        building_id=building.id,
                        data_source_id=source.id,
                        timestamp=timestamp,
                        occupancy_count=occupancy
                    )
                )

        db.commit()

        print("SIMULATED DEMO DATA INSERTED SUCCESSFULLY!")
        print("Buildings:", len(buildings))
        print("Energy readings:", len(buildings) * 96)
        print("Occupancy readings:", len(buildings) * 96)
        print("Weather readings: 96")


if __name__ == "__main__":
    seed_energy_data()
