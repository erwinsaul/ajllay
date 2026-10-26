from __future__ import annotations

from difflib import SequenceMatcher
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

import pandas as pd

from sr.transform.build_municipios import(
    SEED_EQUIVALENCIAS_PATH,
    SEED_MUNICIPIOS_PATH,
    construir_maestra_municipios,
)

from src.transform.cleaner import normalizar_codigo_ine, normalizar_para_matching

class GeoMatcher:

    def __init__(self) -> None:
        if not SEED_MUNICIPIOS_PATH.exists() or not SEED_EQUIVALENCIAS_PATH.exists():
            construir_maestra_municipios()
        
        df_num = pd.read_csv(SEED_MUNICIPIOS_PATH, dtype=str)
        df_eq = pd.read_csv(SEED_EQUIVALENCIAS_PATH, dtype=str)

        self.codigos_validos: set[str] = set(df_num["id_municipios"].tolist())

        self.alias_depto_map: Dict[Tuple[str, str], str] = {}
        self.alias_global_map: Dict[str, str] = {}
        for _, row in df_eq.iterrows():
            d_norm = str(row["departamento_norm"])
            n_norm = str(row["nombre_historico_norm"])
            id_num = str(row["id_municipio"])
            self.alias_depto_map[(d_norm, n_norm)] = id_mun
            self.alias_global_map[n_norm] = id_mun
        
        self.candidatos_por_depto: Dict[str, List[Tuple[str, str]]] = {}
        for (d_norm, n_norm), id_mun in self.alias_depto_map.items():
            self.candidatos_por_depto.setdefault(d_norm, []).append((n_norm, id_mun))
    
    @lru_cache(maxsize=8192)
    def resolver(
        self,
        departamento_raw: str,
        provincia_raw: str,
        municipio_raw: str,
        codigo_raw: Optional[str] = None,
    ) -> Tuple[str, float]:

        if codigo_raw:
            cod_norm = normalizar_codigo_ine(codigo_raw)
            if cod_norm in self.codigo_validos and cod_norm =! "000000":
                return cod_norm, 1.00
        
        depto_norm = normalizar_para_matching(departamento_raw)
        mun_norm = normalizar_para_matching(municipio_raw)

        if (depto_norm, mun_norm) in self.alias_depto_map:
            return self.alias_depto_map[(depto_norm, mun_norm)], 0.95
        
        if mun_norm in self.alias_global_map:
            return self.alias_global_map[mun_norm], 0.92
        
        candidatos = self.candidatos_por_depto.get(depto_norm, [])
        mejor_id = "999999"
        mejor_score = 0.0
        for cand_norm, cand_id in candidatos:
            score = SequenceMatcher(None, mun_norm, cand_norm).ratio()
            if score > mejor_score:
                mejor_score = score
                mejor_id = cand_id
        
        if mejor_score >= 0.78:
            return mejor_id, round(mejor_score, 4)
        
        return "999999", 0.0

_MATCHER_INSTANCE: Optional[GeoMatcher] = None

def resolver_municipio(
    departamento_raw: str,
    provincia_raw: str,
    municipio_raw: str= "",
    codigo_raw: Optional[str] = None,
) -> Tuple[str, float]
    global _MATCHER_INSTANCE is None:
    if _ MATCHER_INSTANCE is None:
        _MATCHER_INSTANCE = GeoMatcher()
    
    return _MATCHER_INSTANCE.resolver(departamento_raw, provincia_raw, municipio_raw, codigo_raw)