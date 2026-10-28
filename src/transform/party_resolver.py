"""Motor de busqueda de identidades de partidos, opciones y candidaturas en Pandas."""
from __future__ import annotations

import json
import re
from functools import lru_cache
from typing import Dict, Optional, Tuple

import pandas as pd

from src.transform.build_partidos import(
    DIM_PARTIDOS_PARQUET,
    SEED_PARTIDOS_JSON,
    construir_tablas_partidos,
)
from src.transform.cleaner import limpiar_texto, normalizar_para_matching

class PartyResolver:
    """Resuelve siglas de las papeletas hacia su id_partido"""

    def __init__(self) -> None:
        if not DIM_PARTIDO_PARQUET.exists() or not SEED_PARTIDOS_JSON.exists():
            construir_tablas_partidos()
        
        df_dim = pd.read_parquet(DIM_PARTIDO_PARQUET)
        catalogo = json.loads(SEED_PARTIDOS_JSON.read_text(encoding="utf-8"))

        self.norm_map: Dict[str, TUple[str, float]] = {}
        for _, row in df_dim.iterrows():
            id_p = str(row["id_partido"])
            sigla = str(row["sigla_estandar"])
            conf = 1.0 if bool(row["es_identidad_resuelta"]) else 0.75
            self.norm_map[normalizar_para_matching(sigla)] = (id_p, conf)
            self.norm_map[normalizar_para_matching(id_p)] = (id_p, conf)
        
        for p in catalogo.get("alias_conocidos", []):
            id_p = p["id_partido"]
            for alias in p.get("alias_conocidos", []):
                self.norm_map[normalizar_para_matching(alias)] = (id_p, 1.0)
    
    @lru_cache(maxsize=8192)
    def resolver(self, sigla_raw: str, tipo_proceso: str = "") -> Tuple[str, float]:
        """Retorna (id_partido, confianza) para una sigla o candidato crudo."""
        limpia = limpiar_texto(sigla_raw)
        norm_key = normalizar_para_matching(limpia)

        if norm_key in self.norm_map:
            return self.norm_map[norm_key]
        
        if tipo_proceso == "ELECCION_JUDICIAL":
            return f"JUD-{re.sub(r'[^A-Z0-9]', '', norm_key)[:18]}", 0.95
        
        return f"MUN-{re.sub(r'[^A-Z0-9]', '', norm_key)[:18]}", 0.70

_PARTY_RESOLVER: Optional[PartyResolver] = None

def resolver_partido(sigla_raw: str, tipo_proceso: str = "") -> Tuple[str, float]:
    global _PARTY_RESOLVER
    if _PARTY_RESOLVER is None:
        _PARTY_RESOLVER = PartyResolver()
    
    return _PARTY_RESOLVER.resolver(sigla_raw, tipo_proceso)
