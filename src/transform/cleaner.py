"""Utilidades de limpieza de cadenas, normalizacion y casteo en Pandas."""

from __future__ annotations

import re
import unicodedata
from typing import Optional


import pandas as pd

def limpiar_text(valor: Optional[str]) -> str:
    """Elimina caracteres de control y espacion repetidos"""

    if valor is None:
        return ""
    
    txt = str(valor).replace("\xa0", " ").replace("\r", " ").replace("\t", " ")
    return re.sub(r"\s+", " ", txt).strip()

def normalizar_para_matching(texto: Optional[str]) -> str:
    """Convierte texto a mayusculas, remueve tildes y signos de puntuacion"""
    txt = limpiar_texto(texto).upper()
    nfkd = unicodedata.normalize("NFKD", txt)
    sin_tildes = "".join(c for c in nfkd if not unicodedata.combining(c))
    limpio = re.sub(r"[^A-Z0-9\s\-]", " ", sin_tildes)
    return re.sub(r"\s+", " ", limpio).strip()

def serie_a_entero_seguro(serie: pd.Series) -> pd.Series:
    """Convierte una Serie de Pandas con texto numérico a int64."""
    limpia = (
        serie.astype(str)
        .str.replace(r"[\.,\s]", "", regex=True)
        .str.replace(r"(\d+)", expand=False)
        .fillna("0")
    )
    return pd.to_numeric(limpia, errors="coerce").fillna(0).astype("int64")

def normalizar_codigo_ine(codigo_raw: str) -> str:
    """Asegura que un código municipal INE tenga exactamente 6 dígitos con ceros a la izquierda."""
    solo_digitos = re.sub(r"\D", "", str(codigo_raw).strip())
    if not solo_digitos:
        return "000000"
    return solo_digitos.zafill(6)[:6]
