import hashlib, json, os, secrets
from datetime import datetime, timedelta, timezone
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import Base, engine, get_db
from app.models import Building
from app.energy_models import EnergyReading
from app.platform_models import User, RefreshToken, ForecastHistory, OptimizationRun, Recommendation, Report, AIExplanationHistory
from app.analytics import get_energy_summary, get_building_energy, get_building_timeseries
from app.anomaly import detect_building_anomalies
from app.schemas import RegisterIn, LoginIn, RefreshIn, PasswordChangeIn, OptimizationIn, ReportIn, ExplainIn
from app.security import create_token, current_user, hash_password, require_roles, verify_password
from app.services import forecast, impact, optimize

Base.metadata.create_all(bind=engine) # additive schema creation, no reset/drop
app=FastAPI(title="WattWise API",description="Campus energy estimates and simulated-data analytics.",version="1.1.0")
app.add_middleware(CORSMiddleware,allow_origins=os.getenv('CORS_ORIGINS','http://localhost:5173').split(','),allow_credentials=False,allow_methods=['*'],allow_headers=['*'])
def out(u): return {'id':u.id,'email':u.email,'full_name':u.full_name,'role':u.role,'is_active':u.is_active}
def issue_refresh(db,u):
 raw=secrets.token_urlsafe(48);db.add(RefreshToken(user_id=u.id,token_hash=hashlib.sha256(raw.encode()).hexdigest(),expires_at=datetime.utcnow()+timedelta(days=7)));return raw
@app.get('/')
def home(): return {'project':'WattWise','status':'online','data_notice':'Demo readings are SIMULATED.'}
@app.get('/api/health')
def health(): return {'status':'healthy'}
@app.post('/api/auth/register',status_code=201)
def register(d:RegisterIn,db:Session=Depends(get_db)):
 if db.query(User).filter_by(email=d.email.lower()).first(): raise HTTPException(409,'Email already registered')
 u=User(email=d.email.lower(),full_name=d.full_name,password_hash=hash_password(d.password));db.add(u);db.commit();db.refresh(u);return out(u)
@app.post('/api/auth/login')
def login(d:LoginIn,db:Session=Depends(get_db)):
 u=db.query(User).filter_by(email=d.email.lower()).first()
 if not u or not u.is_active or not verify_password(d.password,u.password_hash): raise HTTPException(401,'Invalid credentials')
 r=issue_refresh(db,u);db.commit();return {'access_token':create_token({'sub':u.id,'typ':'access','role':u.role},30),'refresh_token':r,'token_type':'bearer','user':out(u)}
@app.post('/api/auth/refresh')
def refresh(d:RefreshIn,db:Session=Depends(get_db)):
 t=db.query(RefreshToken).filter_by(token_hash=hashlib.sha256(d.refresh_token.encode()).hexdigest()).first()
 if not t or t.revoked_at or t.expires_at<datetime.utcnow(): raise HTTPException(401,'Invalid refresh token')
 u=db.get(User,t.user_id)
 if not u or not u.is_active: raise HTTPException(401,'Account unavailable')
 t.revoked_at=datetime.utcnow();r=issue_refresh(db,u);db.commit();return {'access_token':create_token({'sub':u.id,'typ':'access','role':u.role},30),'refresh_token':r,'token_type':'bearer'}
@app.post('/api/auth/logout',status_code=204)
def logout(d:RefreshIn,db:Session=Depends(get_db)):
 t=db.query(RefreshToken).filter_by(token_hash=hashlib.sha256(d.refresh_token.encode()).hexdigest()).first()
 if t:t.revoked_at=datetime.utcnow();db.commit()
@app.get('/api/auth/me')
def me(u=Depends(current_user)):return out(u)
@app.post('/api/auth/change-password',status_code=204)
def password(d:PasswordChangeIn,u=Depends(current_user),db:Session=Depends(get_db)):
 if not verify_password(d.current_password,u.password_hash):raise HTTPException(400,'Current password is incorrect')
 u.password_hash=hash_password(d.new_password);db.query(RefreshToken).filter_by(user_id=u.id,revoked_at=None).update({RefreshToken.revoked_at:datetime.utcnow()});db.commit()
@app.patch('/api/users/{user_id}/active')
def active(user_id:int,is_active:bool,u=Depends(require_roles('ADMIN')),db:Session=Depends(get_db)):
 target=db.get(User,user_id)
 if not target:raise HTTPException(404,'User not found')
 target.is_active=is_active;db.commit();return out(target)
@app.get('/api/campus/summary')
@app.get('/api/energy/summary')
def summary(db:Session=Depends(get_db)):return get_energy_summary(db)
@app.get('/api/buildings')
def buildings(db:Session=Depends(get_db)):return [{'id':x.id,'name':x.name,'building_code':x.building_code,'is_active':x.is_active}for x in db.query(Building).order_by(Building.id)]
@app.get('/api/buildings/{building_id}')
def building(building_id:int,db:Session=Depends(get_db)):
 r=get_building_energy(db,building_id)
 if not r:raise HTTPException(404,'Building not found')
 return r
@app.get('/api/buildings/{building_id}/timeseries')
def timeseries(building_id:int,db:Session=Depends(get_db)):
 r=get_building_timeseries(db,building_id)
 if not r:raise HTTPException(404,'Building not found')
 return r
@app.get('/api/energy/latest')
def latest(db:Session=Depends(get_db)):
 rows=db.query(EnergyReading).order_by(EnergyReading.timestamp.desc()).limit(20);return {'data_status':'SIMULATED','readings':[{'building_id':r.building_id,'timestamp':r.timestamp.isoformat(),'power_kw':float(r.power_kw or 0),'energy_kwh':float(r.energy_kwh)}for r in rows]}
@app.get('/api/alerts')
def alerts(building_id:int|None=None,db:Session=Depends(get_db)):
 ids=[building_id]if building_id else[x.id for x in db.query(Building)];a=[]
 for i in ids:a.extend((detect_building_anomalies(db,i)or{}).get('anomalies',[]))
 return {'data_status':'SIMULATED','alerts':a}
@app.get('/api/forecasts')
def forecasts(building_id:int|None=None,horizon_hours:int=24,u=Depends(current_user),db:Session=Depends(get_db)):
 if not 1<=horizon_hours<=168:raise HTTPException(422,'horizon_hours must be 1-168')
 r=forecast(db,building_id,horizon_hours)
 if not r:raise HTTPException(422,'Insufficient historical readings')
 db.add(ForecastHistory(building_id=building_id,created_by=u.id,method=r['method'],horizon_hours=horizon_hours,result_json=json.dumps(r)));db.commit();return r
@app.post('/api/optimization/runs',status_code=201)
def optimization(d:OptimizationIn,u=Depends(require_roles('ADMIN','FACILITY_MANAGER')),db:Session=Depends(get_db)):
 r=optimize(db,d.building_id)
 if not r:raise HTTPException(404,'Building or readings not found')
 x=OptimizationRun(building_id=d.building_id,requested_by=u.id,baseline_kwh=r['baseline_energy_kwh'],optimized_kwh=r['optimized_energy_kwh'],savings_kwh=r['potential_savings_kwh'],result_json=json.dumps(r));db.add(x);db.flush()
 for y in r['recommendations']:db.add(Recommendation(optimization_run_id=x.id,**y))
 db.commit();return r|{'run_id':x.id}
@app.get('/api/optimization/runs')
def runs(u=Depends(current_user),db:Session=Depends(get_db)):return [{'id':x.id,'building_id':x.building_id,'baseline_kwh':float(x.baseline_kwh),'savings_kwh':float(x.savings_kwh),'created_at':x.created_at}for x in db.query(OptimizationRun).order_by(OptimizationRun.id.desc())]
@app.get('/api/optimization/runs/{run_id}')
def run(run_id:int,u=Depends(current_user),db:Session=Depends(get_db)):
 x=db.get(OptimizationRun,run_id)
 if not x:raise HTTPException(404,'Optimization run not found')
 return json.loads(x.result_json)|{'run_id':x.id}
@app.get('/api/recommendations')
def recommendations(u=Depends(current_user),db:Session=Depends(get_db)):return [{'id':x.id,'optimization_run_id':x.optimization_run_id,'title':x.title,'detail':x.detail,'estimated_savings_kwh':float(x.estimated_savings_kwh),'data_status':'ESTIMATED'}for x in db.query(Recommendation).order_by(Recommendation.id.desc())]
@app.get('/api/impact/summary')
def impacts(u=Depends(current_user),db:Session=Depends(get_db)):return impact(db)
@app.get('/api/reports')
def reports(u=Depends(current_user),db:Session=Depends(get_db)):return [{'id':x.id,'title':x.title,'report_type':x.report_type,'created_at':x.created_at}for x in db.query(Report).order_by(Report.id.desc())]
@app.post('/api/reports',status_code=201)
def report(d:ReportIn,u=Depends(current_user),db:Session=Depends(get_db)):
 content={'campus_summary':get_energy_summary(db),'impact':impact(db),'data_notice':'Energy readings are SIMULATED; impact is ESTIMATED.'};x=Report(created_by=u.id,title=d.title,report_type=d.report_type,content_json=json.dumps(content));db.add(x);db.commit();return {'id':x.id,'content':content}
@app.post('/api/ai/explain')
def explain(d:ExplainIn,u=Depends(current_user),db:Session=Depends(get_db)):
 value={'energy':get_energy_summary(db),'forecast':forecast(db,d.building_id),'optimization':optimize(db,d.building_id)if d.building_id else None,'impact':impact(db),'anomaly':detect_building_anomalies(db,d.building_id)if d.building_id else None}[d.subject]
 if not value:raise HTTPException(422,'Provide available data and building_id where required')
 text=f"Deterministic explanation based only on backend-calculated {d.subject} values. Data status: {value.get('data_status','SIMULATED/ESTIMATED')}. No external AI provider was used and no values were invented."
 db.add(AIExplanationHistory(user_id=u.id,subject=d.subject,explanation=text,input_json=json.dumps(value)));db.commit();return {'provider':'DETERMINISTIC_FALLBACK','explanation':text,'source_values':value}
