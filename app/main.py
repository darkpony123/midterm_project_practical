import os
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
}


def get_conn():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)


app = FastAPI(title="Space Bounty Hunters API")


class HuntCreate(BaseModel):
    criminal_id: int
    success: bool
    notes: str | None = None


class HuntUpdate(BaseModel):
    success: bool | None = None
    notes: str | None = None


# ---------- Wanted criminals ----------

@app.get("/api/criminals/")
def list_criminals(
    min_reward: float | None = None,
    max_reward: float | None = None,
    armed: bool | None = None,
    has_crew: bool | None = None,
    escape_master: bool | None = None,
    sort: str | None = None,
):
    conditions = []
    params = []

    if min_reward is not None:
        conditions.append("reward >= %s")
        params.append(min_reward)
    if max_reward is not None:
        conditions.append("reward <= %s")
        params.append(max_reward)
    if armed is not None:
        conditions.append("armed = %s")
        params.append(armed)
    if has_crew is not None:
        conditions.append("has_crew = %s")
        params.append(has_crew)
    if escape_master is not None:
        conditions.append("escape_master = %s")
        params.append(escape_master)

    if sort is None:
        order = "id"
    elif sort == "reward":
        order = "reward ASC"
    elif sort == "-reward":
        order = "reward DESC"
    else:
        raise HTTPException(status_code=400, detail="sort must be 'reward' or '-reward'")

    query = "SELECT * FROM wanted_criminals"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += f" ORDER BY {order}"

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(query, params)
        return cur.fetchall()


@app.get("/api/criminals/{criminal_id}/")
def get_criminal(criminal_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM wanted_criminals WHERE id = %s", (criminal_id,))
        criminal = cur.fetchone()
    if not criminal:
        raise HTTPException(status_code=404, detail="Criminal not found")
    return criminal


# ---------- Hunt logs ----------

@app.get("/api/hunts/")
def list_hunts(criminal_id: int | None = None):
    with get_conn() as conn, conn.cursor() as cur:
        if criminal_id is not None:
            cur.execute("SELECT * FROM hunt_logs WHERE criminal_id = %s ORDER BY id", (criminal_id,))
        else:
            cur.execute("SELECT * FROM hunt_logs ORDER BY id")
        return cur.fetchall()


@app.get("/api/hunts/{hunt_id}/")
def get_hunt(hunt_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM hunt_logs WHERE id = %s", (hunt_id,))
        hunt = cur.fetchone()
    if not hunt:
        raise HTTPException(status_code=404, detail="Hunt log not found")
    return hunt


@app.post("/api/hunts/", status_code=201)
def create_hunt(hunt: HuntCreate):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id FROM wanted_criminals WHERE id = %s", (hunt.criminal_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=400, detail="Criminal with this id does not exist")
        # created_at is set by the database (DEFAULT NOW()), client can't send it
        cur.execute(
            "INSERT INTO hunt_logs (criminal_id, success, notes) VALUES (%s, %s, %s) RETURNING *",
            (hunt.criminal_id, hunt.success, hunt.notes),
        )
        return cur.fetchone()


@app.patch("/api/hunts/{hunt_id}/")
def update_hunt(hunt_id: int, data: HuntUpdate):
    fields = data.model_dump(exclude_unset=True)
    if not fields:
        raise HTTPException(status_code=400, detail="Provide 'success' and/or 'notes'")
    if "success" in fields and fields["success"] is None:
        raise HTTPException(status_code=400, detail="success can't be null")

    set_part = ", ".join(f"{key} = %s" for key in fields)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            f"UPDATE hunt_logs SET {set_part} WHERE id = %s RETURNING *",
            (*fields.values(), hunt_id),
        )
        updated = cur.fetchone()
    if not updated:
        raise HTTPException(status_code=404, detail="Hunt log not found")
    return updated


@app.delete("/api/hunts/{hunt_id}/", status_code=204)
def delete_hunt(hunt_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM hunt_logs WHERE id = %s RETURNING id", (hunt_id,))
        deleted = cur.fetchone()
    if not deleted:
        raise HTTPException(status_code=404, detail="Hunt log not found")
