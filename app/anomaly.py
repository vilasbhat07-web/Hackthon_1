
from statistics import mean, pstdev

from app.models import Building
from app.energy_models import EnergyReading


def detect_building_anomalies(db, building_id):

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

    if len(readings) < 2:
        return {
            "building_id": building.id,
            "building_name": building.name,
            "data_status": "SIMULATED",
            "message": "Not enough readings for anomaly detection.",
            "anomalies": []
        }

    power_values = [
        float(reading.power_kw)
        for reading in readings
        if reading.power_kw is not None
    ]

    baseline = mean(power_values)
    deviation = pstdev(power_values)

    threshold = baseline + (2 * deviation)

    anomalies = []

    for reading in readings:

        power = float(reading.power_kw or 0)

        if power > threshold:
            anomalies.append({
                "timestamp": reading.timestamp.isoformat(),
                "observed_power_kw": round(power, 2),
                "normal_baseline_kw": round(baseline, 2),
                "threshold_kw": round(threshold, 2),
                "severity": "HIGH",
                "reason": "Power consumption exceeded the statistical baseline.",
                "data_status": "SIMULATED"
            })

    return {
        "building_id": building.id,
        "building_name": building.name,
        "data_status": "SIMULATED",
        "detection_method": "MEAN_PLUS_TWO_STANDARD_DEVIATIONS",
        "baseline_power_kw": round(baseline, 2),
        "anomaly_threshold_kw": round(threshold, 2),
        "total_readings_analyzed": len(readings),
        "total_anomalies": len(anomalies),
        "anomalies": anomalies
    }
