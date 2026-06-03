from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from src.database import init_db, get_connection
from src.models import PacienteCreate, PacienteUpdate, PacienteResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Terapia Holística — Pacientes", lifespan=lifespan)


@app.get("/api/pacientes", response_model=list[PacienteResponse])
def list_pacientes(activo: bool | None = Query(default=None)):
    with get_connection() as conn:
        with conn.cursor() as cur:
            if activo is not None:
                cur.execute(
                    "SELECT * FROM pacientes WHERE activo_sn = %s ORDER BY apellido, nombre",
                    (activo,),
                )
            else:
                cur.execute("SELECT * FROM pacientes ORDER BY apellido, nombre")
            rows = cur.fetchall()
    return [dict(r) for r in rows]


@app.get("/api/pacientes/{paciente_id}", response_model=PacienteResponse)
def get_paciente(paciente_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM pacientes WHERE id = %s", (paciente_id,))
            row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return dict(row)


@app.post("/api/pacientes", response_model=PacienteResponse, status_code=201)
def create_paciente(payload: PacienteCreate):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO pacientes
                    (nombre, apellido, telefono, fecha_nacimiento,
                     historia_clinica, activo_sn, dia_ultima_sesion)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING *
                """,
                (
                    payload.nombre, payload.apellido, payload.telefono,
                    payload.fecha_nacimiento, payload.historia_clinica,
                    payload.activo_sn, payload.dia_ultima_sesion,
                ),
            )
            row = cur.fetchone()
    return dict(row)


@app.patch("/api/pacientes/{paciente_id}", response_model=PacienteResponse)
def update_paciente(paciente_id: int, payload: PacienteUpdate):
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=422, detail="No hay campos para actualizar")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM pacientes WHERE id = %s", (paciente_id,))
            if cur.fetchone() is None:
                raise HTTPException(status_code=404, detail="Paciente no encontrado")

            set_clause = ", ".join(f"{k} = %s" for k in changes)
            set_clause += ", updated_at = NOW()"
            values = list(changes.values()) + [paciente_id]

            cur.execute(
                f"UPDATE pacientes SET {set_clause} WHERE id = %s RETURNING *",
                values,
            )
            row = cur.fetchone()
    return dict(row)


@app.delete("/api/pacientes/{paciente_id}", status_code=204)
def delete_paciente(paciente_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM pacientes WHERE id = %s", (paciente_id,))
            if cur.fetchone() is None:
                raise HTTPException(status_code=404, detail="Paciente no encontrado")
            cur.execute("DELETE FROM pacientes WHERE id = %s", (paciente_id,))
