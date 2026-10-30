# WattWise backend

WattWise is a FastAPI demonstration backend. The bundled energy, occupancy, and weather readings are **SIMULATED**. Forecasts, optimization outcomes, cost, and carbon values are **ESTIMATED** and must not be interpreted as meter data or physical appliance control.

## Run

```cmd
cd D:\WattWise\backend
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
REM Set JWT_SECRET in .env to a long random value before production use
python -m app.init_db
uvicorn app.main:app --reload --port 8000
```

The existing `data\wattwise.db` is retained. `init_db` only creates missing tables. Do not run the seed scripts if you need to preserve a modified demo dataset.

Open API documentation at `http://localhost:8000/docs`.

## Roles

Registration creates a `VIEWER`. There is deliberately no default administrator account or password. Promote the first approved user through a controlled local/admin process. `ADMIN` can activate/deactivate accounts; `ADMIN` and `FACILITY_MANAGER` can create optimization runs. All other protected read endpoints accept any authenticated active user.
