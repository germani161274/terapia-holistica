import os
import streamlit as st
import requests
from datetime import date, datetime

API_BASE = os.getenv("API_BASE", "https://terapia-holistica-1.onrender.com/api/pacientes")

st.set_page_config(
    page_title="Terapia Holística",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
/* ── fondos ────────────────────────────────────────── */
[data-testid="stAppViewContainer"] { background-color: #071e34; }
[data-testid="stHeader"]            { background-color: #071e34; }
[data-testid="stSidebar"]           { background-color: #04111f; border-right: 1px solid #153450; }
[data-testid="stMain"]              { background-color: #071e34; }

/* ── tipografía ────────────────────────────────────── */
html, body, [class*="css"]   { color: #cdd9e5; }
h1, h2, h3, h4               { color: #ffffff !important; }
p                            { color: #b0c4d8; }
label                        { color: #7faec8 !important; }
small                        { color: #7faec8; }

/* ── métricas ──────────────────────────────────────── */
[data-testid="metric-container"] {
    background-color: #0d2b44;
    border: 1px solid #1b4870;
    border-radius: 10px;
    padding: 14px 18px;
}
[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 2rem !important; }
[data-testid="stMetricLabel"] { color: #6fa8c8 !important; }

/* ── expanders ─────────────────────────────────────── */
[data-testid="stExpander"] {
    background-color: #0d2b44;
    border: 1px solid #1b4870;
    border-radius: 10px;
    margin-bottom: 6px;
}
[data-testid="stExpander"] > div:first-child {
    color: #e0f0ff !important;
    font-weight: 500;
}

/* ── inputs ────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea  > div > div > textarea,
.stDateInput > div > div > input {
    background-color: #0a2035 !important;
    color: #e0ecf8 !important;
    border: 1px solid #1e4d78 !important;
    border-radius: 6px !important;
}
.stTextInput > div > div > input::placeholder,
.stTextArea  > div > div > textarea::placeholder { color: #4a7a9b !important; }

/* ── checkbox ──────────────────────────────────────── */
[data-testid="stCheckbox"] label { color: #b0c8e0 !important; }

/* ── botones ───────────────────────────────────────── */
.stButton > button,
.stFormSubmitButton > button {
    background-color: #1565c0 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 6px !important;
}
.stButton > button:hover,
.stFormSubmitButton > button:hover { background-color: #1976d2 !important; }

/* ── divider ───────────────────────────────────────── */
hr { border-color: #153450 !important; }

/* ── radio ─────────────────────────────────────────── */
[data-testid="stRadio"] label { color: #b0c8e0 !important; }
</style>
""", unsafe_allow_html=True)


# ── helpers API ──────────────────────────────────────────────────────────────

def api_get(url, **params):
    try:
        r = requests.get(
            url,
            params={k: v for k, v in params.items() if v is not None},
            timeout=5,
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("⚠️ No se puede conectar con la API. Verificá que uvicorn esté corriendo en el puerto 8000.")
        return None


def api_post(url, data):
    r = requests.post(url, json=data, timeout=5)
    r.raise_for_status()
    return r.json()


def api_patch(url, data):
    r = requests.patch(url, json=data, timeout=5)
    r.raise_for_status()
    return r.json()


def api_delete(url):
    r = requests.delete(url, timeout=5)
    r.raise_for_status()


def to_date(value):
    """Convert ISO string or datetime to date, or return None."""
    if value is None:
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except (ValueError, TypeError):
        return None


def to_iso(value):
    """Convert date to ISO string or return None."""
    if value is None:
        return None
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return str(value) if value else None


def fmt_date(value):
    """Format ISO date string or date object as dd/MM/yyyy for display."""
    d = to_date(value)
    if d is None:
        return ""
    return d.strftime("%d/%m/%Y")


# ── título ───────────────────────────────────────────────────────────────────

st.markdown("# 🌿 Terapia Holística")
st.markdown("##### Gestión de Pacientes")
st.divider()


# ── sidebar: filtros + nuevo paciente ────────────────────────────────────────

with st.sidebar:
    st.markdown("### 👤 Nuevo paciente")
    with st.form("nuevo_paciente", clear_on_submit=True):
        np_nombre     = st.text_input("Nombre *")
        np_apellido   = st.text_input("Apellido *")
        np_telefono   = st.text_input("Teléfono")
        np_nacimiento = st.date_input("Fecha de nacimiento", value=None,
                                     min_value=date(1930, 1, 1), format="DD/MM/YYYY")
        np_activo     = st.checkbox("Activo", value=True)
        np_ult_sesion = st.date_input("Día última sesión", value=None, format="DD/MM/YYYY")
        np_historia   = st.text_area("Historia clínica", height=100)
        registrar     = st.form_submit_button("➕ Registrar paciente", use_container_width=True)

    if registrar:
        if not np_nombre.strip() or not np_apellido.strip():
            st.error("Nombre y apellido son obligatorios.")
        else:
            try:
                api_post(API_BASE, {
                    "nombre":            np_nombre.strip(),
                    "apellido":          np_apellido.strip(),
                    "telefono":          np_telefono.strip() or None,
                    "fecha_nacimiento":  to_iso(np_nacimiento),
                    "activo_sn":         np_activo,
                    "dia_ultima_sesion": to_iso(np_ult_sesion),
                    "historia_clinica":  np_historia.strip() or None,
                })
                st.success(f"✅ {np_nombre} {np_apellido} registrado.")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    st.divider()
    st.markdown("### 🔍 Filtros")
    filtro = st.radio(
        "Mostrar",
        ["Todos", "Solo activos", "Solo inactivos"],
        index=1,
    )
    buscar = st.text_input("Buscar nombre o apellido")


# ── obtener pacientes ─────────────────────────────────────────────────────────

activo_param = None
if filtro == "Solo activos":
    activo_param = "true"
elif filtro == "Solo inactivos":
    activo_param = "false"

result = api_get(API_BASE, activo=activo_param)
if result is None:
    st.stop()

pacientes = result
if buscar:
    term = buscar.lower()
    pacientes = [
        p for p in pacientes
        if term in p["nombre"].lower() or term in p["apellido"].lower()
    ]

all_pacientes = api_get(API_BASE) or []


# ── métricas ──────────────────────────────────────────────────────────────────

total     = len(all_pacientes)
activos   = sum(1 for p in all_pacientes if p["activo_sn"])
inactivos = total - activos
mostrando = len(pacientes)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total pacientes", total)
c2.metric("Activos",         activos)
c3.metric("Inactivos",       inactivos)
c4.metric("Mostrando",       mostrando)

st.divider()


# ── listado ───────────────────────────────────────────────────────────────────

st.markdown("### 📋 Listado de pacientes")

if not pacientes:
    st.info("No hay pacientes para mostrar con el filtro actual.")
else:
    for p in pacientes:
        icono      = "🟢" if p["activo_sn"] else "🔴"
        tel_txt    = f" · 📞 {p['telefono']}"              if p["telefono"]          else ""
        sesion_txt = f" · Última sesión: {fmt_date(p['dia_ultima_sesion'])}" if p["dia_ultima_sesion"] else ""
        label      = f"{icono} **{p['apellido']}, {p['nombre']}**{tel_txt}{sesion_txt}  `ID {p['id']}`"

        with st.expander(label):

            # ── formulario de edición ──────────────────────────────────────
            with st.form(f"edit_{p['id']}"):
                col1, col2 = st.columns(2)
                e_nombre   = col1.text_input("Nombre *",   value=p["nombre"],   key=f"n_{p['id']}")
                e_apellido = col2.text_input("Apellido *", value=p["apellido"], key=f"a_{p['id']}")

                col3, col4 = st.columns(2)
                e_telefono   = col3.text_input(
                    "Teléfono", value=p["telefono"] or "", key=f"t_{p['id']}"
                )
                e_nacimiento = col4.date_input(
                    "Fecha de nacimiento",
                    value=to_date(p["fecha_nacimiento"]),
                    min_value=date(1930, 1, 1),
                    format="DD/MM/YYYY",
                    key=f"fn_{p['id']}",
                )

                col5, col6 = st.columns(2)
                e_activo    = col5.checkbox(
                    "Activo", value=p["activo_sn"], key=f"ac_{p['id']}"
                )
                e_ult_sesion = col6.date_input(
                    "Día última sesión",
                    value=to_date(p["dia_ultima_sesion"]),
                    format="DD/MM/YYYY",
                    key=f"us_{p['id']}",
                )

                e_historia = st.text_area(
                    "Historia clínica",
                    value=p["historia_clinica"] or "",
                    height=260,
                    key=f"hc_{p['id']}",
                )

                guardar = st.form_submit_button("💾 Guardar cambios", use_container_width=True)

            # ── botón eliminar (fuera del form) ────────────────────────────
            if st.button("🗑️ Eliminar paciente", key=f"del_{p['id']}"):
                try:
                    api_delete(f"{API_BASE}/{p['id']}")
                    st.success("Paciente eliminado.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

        # ── procesar guardado ──────────────────────────────────────────────
        if guardar:
            if not e_nombre.strip() or not e_apellido.strip():
                st.error("Nombre y apellido son obligatorios.")
            else:
                try:
                    api_patch(f"{API_BASE}/{p['id']}", {
                        "nombre":            e_nombre.strip(),
                        "apellido":          e_apellido.strip(),
                        "telefono":          e_telefono.strip() or None,
                        "fecha_nacimiento":  to_iso(e_nacimiento),
                        "activo_sn":         e_activo,
                        "dia_ultima_sesion": to_iso(e_ult_sesion),
                        "historia_clinica":  e_historia.strip() or None,
                    })
                    st.success("✅ Cambios guardados correctamente.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")
