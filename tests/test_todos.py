import os
import pytest
import psycopg2
from fastapi.testclient import TestClient
from src import database
from src.main import app

# Usa TEST_DATABASE_URL si existe; sino la misma DATABASE_URL pero en db _test
database.DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/terapia_holistica_test",
)

client = TestClient(app)


# ── fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def fresh_db():
    try:
        database.init_db()
    except psycopg2.OperationalError as e:
        pytest.skip(f"PostgreSQL no disponible: {e}")
    conn = psycopg2.connect(database.DATABASE_URL)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE pacientes RESTART IDENTITY")
    conn.close()
    yield


def _crear(nombre="Ana", apellido="García", **kwargs):
    data = {"nombre": nombre, "apellido": apellido, **kwargs}
    return client.post("/api/pacientes", json=data)


# ── GET /api/pacientes ────────────────────────────────────────────────────────

def test_listar_vacio():
    r = client.get("/api/pacientes")
    assert r.status_code == 200
    assert r.json() == []


def test_listar_todos():
    _crear("Ana", "García")
    _crear("Luis", "Pérez")
    r = client.get("/api/pacientes")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_listar_filtro_activo():
    id1 = _crear("Ana", "García").json()["id"]
    _crear("Luis", "Pérez")
    client.patch(f"/api/pacientes/{id1}", json={"activo_sn": False})

    activos   = client.get("/api/pacientes?activo=true").json()
    inactivos = client.get("/api/pacientes?activo=false").json()

    assert len(activos) == 1 and activos[0]["activo_sn"] is True
    assert len(inactivos) == 1 and inactivos[0]["activo_sn"] is False


# ── GET /api/pacientes/{id} ───────────────────────────────────────────────────

def test_obtener_paciente_ok():
    creado = _crear("María", "López", telefono="1234567890").json()
    r = client.get(f"/api/pacientes/{creado['id']}")
    assert r.status_code == 200
    data = r.json()
    assert data["nombre"] == "María"
    assert data["telefono"] == "1234567890"
    assert data["activo_sn"] is True


def test_obtener_paciente_no_encontrado():
    assert client.get("/api/pacientes/9999").status_code == 404


# ── POST /api/pacientes ───────────────────────────────────────────────────────

def test_crear_minimo():
    r = _crear("Carlos", "Sánchez")
    assert r.status_code == 201
    d = r.json()
    assert d["nombre"] == "Carlos"
    assert d["apellido"] == "Sánchez"
    assert d["activo_sn"] is True
    assert "id" in d


def test_crear_completo():
    r = _crear(
        "Julia", "Martínez",
        telefono="5551234",
        fecha_nacimiento="1990-05-15",
        historia_clinica="Paciente con estrés crónico.",
        activo_sn=True,
        dia_ultima_sesion="2026-05-20",
    )
    assert r.status_code == 201
    d = r.json()
    assert d["telefono"] == "5551234"
    assert d["historia_clinica"] == "Paciente con estrés crónico."
    assert d["dia_ultima_sesion"] == "2026-05-20"


def test_crear_sin_nombre_falla():
    r = client.post("/api/pacientes", json={"apellido": "García"})
    assert r.status_code == 422


def test_crear_nombre_vacio_falla():
    r = client.post("/api/pacientes", json={"nombre": "", "apellido": "García"})
    assert r.status_code == 422


# ── PATCH /api/pacientes/{id} ─────────────────────────────────────────────────

def test_actualizar_nombre():
    pid = _crear("Pedro", "Ruiz").json()["id"]
    r = client.patch(f"/api/pacientes/{pid}", json={"nombre": "Pablo"})
    assert r.status_code == 200
    assert r.json()["nombre"] == "Pablo"


def test_actualizar_historia_clinica():
    pid = _crear("Rosa", "Vega").json()["id"]
    r = client.patch(f"/api/pacientes/{pid}", json={"historia_clinica": "Nueva historia."})
    assert r.status_code == 200
    assert r.json()["historia_clinica"] == "Nueva historia."


def test_desactivar_paciente():
    pid = _crear("Sofía", "Díaz").json()["id"]
    r = client.patch(f"/api/pacientes/{pid}", json={"activo_sn": False})
    assert r.status_code == 200
    assert r.json()["activo_sn"] is False


def test_actualizar_no_encontrado():
    r = client.patch("/api/pacientes/9999", json={"nombre": "Fantasma"})
    assert r.status_code == 404


def test_actualizar_sin_campos_falla():
    pid = _crear("Tom", "Álvarez").json()["id"]
    r = client.patch(f"/api/pacientes/{pid}", json={})
    assert r.status_code == 422


# ── DELETE /api/pacientes/{id} ────────────────────────────────────────────────

def test_eliminar_ok():
    pid = _crear("Elena", "Mora").json()["id"]
    r = client.delete(f"/api/pacientes/{pid}")
    assert r.status_code == 204
    assert client.get(f"/api/pacientes/{pid}").status_code == 404


def test_eliminar_no_encontrado():
    assert client.delete("/api/pacientes/9999").status_code == 404
