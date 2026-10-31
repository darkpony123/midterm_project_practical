# Space Bounty Hunters API

REST API for bounty hunters: a database of wanted criminals and a journal of hunt attempts.
Stack: FastAPI (Python) + PostgreSQL, running in Docker.

## Run

```
docker compose up --build
```

API: `http://localhost:8000`, Swagger: `http://localhost:8000/docs`

## Database setup / import

The database is created and filled automatically. `db/init.sql` is mounted into
`/docker-entrypoint-initdb.d/`, so Postgres runs it on the first start (empty volume).
It creates both tables and inserts 7 criminals and 11 hunt logs.

To reset the database to the initial data:
```
docker compose down -v
docker compose up --build
```

## Models

**wanted_criminals**: id, name (nullable, may be unknown), nickname, reward, latitude, longitude
(nullable), location_note (nullable), difficulty (1-10), armed, has_crew, escape_master.

**hunt_logs**: id, criminal_id (FK to wanted_criminals), success, notes, created_at (set by the server, `DEFAULT NOW()`).

Relationship: one criminal has many hunt logs (one-to-many through `criminal_id`).

## Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/criminals/` | List criminals. Query: `min_reward`, `max_reward`, `armed`, `has_crew`, `escape_master`, `sort` (`reward` / `-reward`). Filters combine. |
| GET | `/api/criminals/{id}/` | One criminal (404 if not found) |
| GET | `/api/hunts/` | List hunt logs. Query: `criminal_id` |
| GET | `/api/hunts/{id}/` | One hunt log (404) |
| POST | `/api/hunts/` | Create hunt log (201). 400 if criminal doesn't exist, 422 if body invalid |
| PATCH | `/api/hunts/{id}/` | Update `success` and/or `notes` (404, 400) |
| DELETE | `/api/hunts/{id}/` | Delete hunt log (204, 404) |

Example: `GET /api/criminals/?min_reward=5000&armed=true&sort=-reward`

POST body:
```json
{ "criminal_id": 3, "success": false, "notes": "Target escaped through an asteroid field." }
```

## Postman

Import `postman_collection.json`. Variable `baseUrl` = `http://localhost:8000`.
"Create hunt log" saves the new id to `huntId`, so run it before get/update/delete.
