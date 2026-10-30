
from sqlalchemy import func

from app.models import Building
from app.energy_models import EnergyReading, OccupancyReading


# 1. CAMPUS-WIDE ENERGY SUMMARY

def get_energy_summary(db):

    total_energy = (
        db.query(func.sum(EnergyReading.energy_kwh)).scalar() or 0
    )

    peak_power = (
        db.query(func.sum(EnergyReading.power_kw))
        .group_by(EnergyReading.timestamp)
        .order_by(func.sum(EnergyReading.power_kw).desc())
        .limit(1)
        .scalar() or 0
    )

    average_occupancy = (
        db.query(func.avg(OccupancyReading.occupancy_count)).scalar() or 0
    )

    total_readings = db.query(EnergyReading).count()

    building_results = (
        db.query(
            Building.id,
            Building.name,
            func.sum(EnergyReading.energy_kwh).label("total_energy"),
            func.max(EnergyReading.power_kw).label("peak_power"),
        )
        .join(
            EnergyReading,
            EnergyReading.building_id == Building.id
        )
        .group_by(Building.id, Building.name)
        .all()
    )

    buildings = []

    for building in building_results:
        buildings.append({
            "building_id": building.id,
            "building_name": building.name,
            "energy_kwh": round(float(building.total_energy or 0), 2),
            "peak_power_kw": round(float(building.peak_power or 0), 2),
        })

    return {
        "data_status": "SIMULATED",
        "total_energy_kwh": round(float(total_energy), 2),
        "peak_campus_demand_kw": round(float(peak_power), 2),
        "average_occupancy": round(float(average_occupancy), 2),
        "total_energy_readings": total_readings,
        "building_breakdown": buildings,
    }


# 2. INDIVIDUAL BUILDING ENERGY SUMMARY

def get_building_energy(db, building_id):

    building = db.query(Building).filter(
        Building.id == building_id
    ).first()

    if building is None:
        return None

    energy = (
        db.query(func.sum(EnergyReading.energy_kwh))
        .filter(EnergyReading.building_id == building_id)
        .scalar() or 0
    )

    peak = (
        db.query(func.max(EnergyReading.power_kw))
        .filter(EnergyReading.building_id == building_id)
        .scalar() or 0
    )

    occupancy = (
        db.query(func.avg(OccupancyReading.occupancy_count))
        .filter(OccupancyReading.building_id == building_id)
        .scalar() or 0
    )

    return {
        "building_id": building.id,
        "building_name": building.name,
        "data_status": "SIMULATED",
        "energy_kwh": round(float(energy), 2),
        "peak_power_kw": round(float(peak), 2),
        "average_occupancy": round(float(occupancy), 2),
    }


# 3. BUILDING ENERGY TIME SERIES

def get_building_timeseries(db, building_id):

    building = db.query(Building).filter(
        Building.id == building_id
    ).first()

    if building is None:
        return None

    readings = (
        db.query(EnergyReading)
        .filter(EnergyReading.building_id == building_id)
        .order_by(EnergyReading.timestamp.asc())
        .all()
    )

    data = []

    for reading in readings:
        data.append({
            "timestamp": reading.timestamp.isoformat(),
            "power_kw": round(float(reading.power_kw or 0), 2),
            "energy_kwh": round(float(reading.energy_kwh), 4),
            "data_status": "SIMULATED"
        })

    return {
        "building_id": building.id,
        "building_name": building.name,
        "interval_minutes": 15,
        "total_readings": len(data),
        "data_status": "SIMULATED",
        "data": data
    }
