"""Esquema de la capa de Staging para Pandas y Pydantiv."""

from __future__ import annotations

from typing import Final, List

from pydantic import BaseModel, Field

STAGING_COLUMNS: Final[List[str]] = [
    "id_eleccion",
    "anio",
    "tipo_proceso",
    "subtipo_proceso",
    "codigo_municipio_raw",
    "departamento_raw",
    "municipio_raw",
    "total_mesas",
    "sigla_partido_raw",
    "votos_partido",
    "votos_validos_total",
    "votos_blancos",
    "votos_nulos",
    "votos_emitidos",
    "inscritos_habilitados",
]

STAGING_PANDAS_DTYPES: Final[dict[str, str]] = {
    "id_eleccion": "string",
    "anio": "int32",
    "tipo_proceso": "string",
    "subtipo_proceso": "string",
    "codigo_municipio_raw": "string",
    "departamento_raw": "string",
    "provincia_raw": "string",
    "municipio_raw": "string",
    "total_mesas": "int64",
    "sigla_partido_raw": "string",
    "votos_partido": "int64",
    "votos_validos_total": "int64",
    "votos_blancos": "int64",
    "votos_nulos": "int64",
    "votos_emitidos": "int64",
    "inscritos_habilitados": "int64",
}

class StagingRowContract(BaseModel):
    
    id_eleccion:str
    anio: int = Field(..., ge=1979, le=2025)
    tipo_proceso: str
    subtipo_proceso:str
    codigo_municipio_raw: str
    departamento_raw: str
    provincia_raw: str
    municipio_raw: str
    total_mesas: int = Field(..., ge=1)
    sigla_partido_raw: str
    votos_partido: int = Field(..., ge=0)
    votos_validos_total: int = Field(..., ge=0)
    votos_blancos: int = Field(..., ge=0)
    votos_nulos: int = Field(..., ge=0)
    votos_emitidos: int = Field(..., ge=0)
    inscritos_habilitados: int = Field(..., ge=0)


