# FakeGuard microservices

| Service | Port | Public-compatible endpoints | Responsibility |
| --- | --- | --- | --- |
| prediction-service | 8000 | `GET /`, `POST /predict`, `POST /predict/bulk`, `GET /model-info`, `GET /metrics` | Loads the existing Instagram and Twitter models and persists results through History Service. |
| history-service | 8001 | `GET /`, `POST /records`, `GET /history`, `DELETE /history/clear` | Owns the PostgreSQL prediction history. `POST /records` is internal. |
| analytics-service | 8002 | `GET /`, `GET /dashboard` | Builds dashboard data through History Service's public API. |

All services use HTTP and configurable environment variables. `HISTORY_SERVICE_URL` defaults to `http://history-service:8001`; `DATABASE_URL` is required by History Service.

## Local development

Create an optional `.env` containing a non-default `POSTGRES_PASSWORD`, then run `docker compose up --build`. The `fakeguard-postgres-data` volume stores new history safely across container recreation. The legacy SQLite database is never removed or altered.

The former monolithic backend remains available temporarily as an opt-in compatibility profile on port `8003`:

```powershell
docker compose --profile legacy up --build legacy-backend
```

To migrate legacy data after the stack is healthy:

```powershell
$env:DATABASE_URL = "postgresql://fakeguard:<password>@localhost:5432/fakeguard"
python services/history-service/migrate_sqlite.py backend/predictions.db
```

This is intentionally manual and append-only; back up the PostgreSQL volume and avoid running it twice unless duplicate history is desired.

## Kubernetes database secret

Create the referenced Secret before `kubernetes/microservices.yaml`:

```powershell
kubectl create secret generic fakeguard-database `
  --from-literal=database=fakeguard `
  --from-literal=username=fakeguard `
  --from-literal=password='<choose-a-strong-password>' `
  --from-literal=url='postgresql://fakeguard:<choose-a-strong-password>@postgres-service:5432/fakeguard'
```
