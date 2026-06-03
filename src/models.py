from __future__ import annotations
from datetime import date, datetime
from pydantic import BaseModel, Field


class PacienteCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    apellido: str = Field(..., min_length=1, max_length=100)
    telefono: str | None = None
    fecha_nacimiento: date | None = None
    historia_clinica: str | None = None
    activo_sn: bool = True
    dia_ultima_sesion: date | None = None


class PacienteUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    apellido: str | None = Field(default=None, min_length=1, max_length=100)
    telefono: str | None = None
    fecha_nacimiento: date | None = None
    historia_clinica: str | None = None
    activo_sn: bool | None = None
    dia_ultima_sesion: date | None = None


class PacienteResponse(BaseModel):
    id: int
    nombre: str
    apellido: str
    telefono: str | None
    fecha_nacimiento: date | None
    historia_clinica: str | None
    activo_sn: bool
    dia_ultima_sesion: date | None
    created_at: datetime
    updated_at: datetime
