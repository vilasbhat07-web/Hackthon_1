from collections import defaultdict
from datetime import timedelta
from sqlalchemy import func
from app.energy_models import EnergyReading, OccupancyReading
from app.models import Building

def forecast(db, building_id=None, horizon_hours=24):
    q=db.query(EnergyReading).order_by(EnergyReading.timestamp)
    if building_id: q=q.filter(EnergyReading.building_id==building_id)
    rows=q.all()
    if len(rows)<4: return None
    buckets=defaultdict(list)
    for r in rows: buckets[(r.timestamp.hour,r.timestamp.minute)].append(float(r.power_kw or 0))
    last=rows[-1].timestamp; interval=rows[-1].interval_minutes
    points=[]
    for n in range(max(1, horizon_hours*60//interval)):
        ts=last+timedelta(minutes=interval*(n+1)); power=sum(buckets[(ts.hour,ts.minute)])/len(buckets[(ts.hour,ts.minute)])
        points.append({"timestamp":ts.isoformat(),"estimated_power_kw":round(power,3),"estimated_energy_kwh":round(power*interval/60,4),"data_status":"ESTIMATED"})
    return {"method":"TIME_OF_DAY_HISTORICAL_MEAN","limitations":"Baseline estimate from available simulated historical readings; it does not model weather, holidays, or future schedule changes.","data_status":"ESTIMATED","building_id":building_id,"horizon_hours":horizon_hours,"points":points}

def optimize(db, building_id):
    building=db.get(Building,building_id)
    rows=db.query(EnergyReading).filter(EnergyReading.building_id==building_id).all()
    if not building or not rows: return None
    baseline=sum(float(x.energy_kwh) for x in rows)
    off_hours=[x for x in rows if x.timestamp.hour < 8 or x.timestamp.hour >= 17]
    avoidable=sum(float(x.energy_kwh) for x in off_hours)*0.15
    return {"building_id":building_id,"building_name":building.name,"method":"DETERMINISTIC_OFF_HOURS_REDUCTION","data_status":"ESTIMATED","assumption":"A 15% avoidable-load reduction during low-occupancy hours; no equipment is controlled.","baseline_energy_kwh":round(baseline,4),"optimized_energy_kwh":round(baseline-avoidable,4),"potential_savings_kwh":round(avoidable,4),"energy_savings_percent":round(avoidable/baseline*100,2),"recommendations":[{"title":"Review off-hours schedules","detail":"Schedule non-essential HVAC, lighting, and plug loads around occupancy; validate with facilities staff.","estimated_savings_kwh":round(avoidable,4)}]}

def impact(db):
    from app.platform_models import ElectricityTariff, CarbonEmissionFactor, OptimizationRun
    energy=float(db.query(func.sum(EnergyReading.energy_kwh)).scalar() or 0)
    tariff=db.query(ElectricityTariff).filter_by(is_active=True).first(); factor=db.query(CarbonEmissionFactor).filter_by(is_active=True).first()
    rate=float(tariff.rate_per_kwh) if tariff else 8.0; carbon=float(factor.kg_co2e_per_kwh) if factor else .82
    savings=float(db.query(func.sum(OptimizationRun.savings_kwh)).scalar() or 0)
    return {"data_status":"ESTIMATED","assumptions":{"tariff_inr_per_kwh":rate,"carbon_kg_co2e_per_kwh":carbon},"energy_kwh":round(energy,2),"estimated_cost_inr":round(energy*rate,2),"estimated_carbon_kg_co2e":round(energy*carbon,2),"potential_savings_kwh":round(savings,2),"potential_cost_savings_inr":round(savings*rate,2),"potential_carbon_savings_kg_co2e":round(savings*carbon,2)}
