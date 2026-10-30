# Frontend integration

Base URL in local development: `http://localhost:8000`. Configure Vite with `VITE_API_URL=http://localhost:8000`.

Register with `POST /api/auth/register`, then login with `POST /api/auth/login`. Put the returned access token in `Authorization: Bearer <access_token>`. Store the refresh token securely and rotate it through `POST /api/auth/refresh`; revoke it with `POST /api/auth/logout`.

Public dashboard endpoints: `/api/campus/summary`, `/api/buildings`, `/api/buildings/{id}`, `/api/buildings/{id}/timeseries`, `/api/energy/summary`, `/api/energy/latest`, and `/api/alerts`.

Authenticated intelligence endpoints: `/api/forecasts`, `/api/recommendations`, `/api/impact/summary`, `/api/reports`, and `/api/ai/explain`. A facility manager or admin can call `POST /api/optimization/runs` with `{"building_id": 1}`. Responses explicitly contain `SIMULATED` or `ESTIMATED` status where applicable.
