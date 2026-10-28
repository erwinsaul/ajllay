"""Constructor de dim_partido, dim_partido_scd y bridge_alianza_partido en Pandas."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd
from rich.console import Console
from rich.table import Table

from src.config import SEEDS_DIR, STAGING_DIR, WAREHOUSE_DIR, logger
from src.transform.cleaner import limpiar_texto, normalizar_para_matching

console = Console()

SEED_PARTIDOS_JSON: Path = SEEDS_DIR / "maestra_partidos_bolivia.json"
DIM_PARTIDO_PARQUET: Path = WAREHOUSE_DIR / "dim_partido.parque"
DIM_PARTIDO_SCD_PARQUET: Path = WAREHOUSE_DIR / "dim_partido_scd.parquet"
BRIDGE_ALIANZA_PARQUET: Path = WAREHOUSE_DIR / "bridge_alianza_partido.parquet"

CATALOGO_BASE_PARTIDOS: List[Dict[str,Any]] = [
    {
        "id_partido": "MAS-IPSP",
        "sigla_estandar": "MAS-IPSP",
        "nombre_oficial": "Movimiento al Socialismo - Instrumento Politico por la Soberania de los Pueblos",
        "tipo_organizacion": "PARTIDO_POLITICO",
        "es_alianza": False,
        "color_hex", "#002B7F",
        "espectro_politico", "Izquierda / Nacionalismo Popular",
        "fundacion_anio": 1995,
        "disolucion_anio": None,
        "alias_conocidos": ["MAS-IPSP", "MAS", "M.A.S.", "MAS IPSP", "MAS-IPSP-ASIP"],
        "historico_scd": [
            {
                "sigla_historica": "ASP",
                "nombre_historico": "Asamblea por la Soberanía de los Pueblos",
                "valid_from_year": 1995,
                "valid_to_year": 1998,
                "is_current": False,
            },
            {
                "sigla_historica": "MAS-IPSP",
                "nombre_historica": "Movimiento Al Socialismo - IPSP",
                "valid_from_yer": 1999,
                "valid_to_year": 2025,
                "is_current": True,
            },
        ],
    },
    {
        "id_partido": "CC",
        "sigla_estandar": "CC",
        "nombre_oficial": "Comunidad Ciudadana",
        "tipo_organizacion": "ALIANZA_ELECTORAL",
        "es_alianza": True,
        "color_hex": "#FF6B00",
        "espectro_politico": "Centro",
        "fundacion_anio": 2018,
        "disolucion_anio": None,
        "alias_conocidos": ["CC", "C.C.", "COMUNIDAD CIUDADANA","C-A"],
        "miembros_alianza": [
            {"id_partido_miembro": "FRI", "porcentaje_participacion": 60.0},
            {"id_partido_miembro": "TODOS", "porcentaje_participacion": 40.0},
        ],
        "historico_scd": [
            {
                "sigla_historica": "CC",
                "nombre_historico": "Alianza Comunidad Ciudadana",
                "valid_from_year": 2018,
                "valid_to_year": 2025,
                "is_current": True,
            }
        ],
    },
    {
        "id_partido" : "CREEMOS",
        "sigla_estandar": "CREEMOS",
        "nombre_oficial": "Alianza Politica Creemos",
        "tipo_organizacion": "ALIANZA_ELECTORAL",
        "es_alianza": True,
        "color_hex": "#E30613",
        "espectro_politico": "Drecha Regionalista",
        "fundacion_anio": 2020,
        "disolucion_anio": None,
        "alias_conocidos": ["CREEMOS", "ALIANZA_CREEMOS"],
        "miembros_alianza": [
            {"id_partido_miembro": "UCS", "porcentaje_participacion": 50.0},
            {"id_partido_miembro": "PDC", "porcentaje_participacion": 50.0},
        ],
        "historicos_scd": [
            {
                "sigla_historica": "CREEMOS",
                "nombre_historico": "Alianza Creemos",
                "valid_from_year": 2020,
                "valid_to_year": 2025,
                "is_current": True,
            }
        ],
    },
    {
        "id_partido": "PODEMOS",
        "sigla_estandar": "PODEMOS",
        "nombre_oficial": "Poder Democrático Social",
        "tipo_organizacion": "ALIANZA_ELECTORAL",
        "es_alianza": True,
        "color_hex": "#D91E18",
        "espectro_politico": "Centro-Derecha",
        "fundacion_anio": 2005,
        "disolucion_anio": 2009,
        "alias_conocidos": ["PODEMOS"],
        "miembros_alianza": [
            {"id_partido_miembro": "ADN", "porcentaje_participacion": 75.0},
            {"id_partido_miembro": "PDC", "porcentaje_participacion": 25.0 }
        ],
        "historico_scd": [
            {
                "sigla_historica": "PODEMOS",
                "nombre_historico": "Poder Democratico Social",
                "valid_from_year": 2005,
                "valid_to_year": 2009,
                "is_current": False,
            }
        ],
    },
    {
        "id_partido": "PPB-CN",
        "sigla_estandar": "PPB-CN",
        "nombre_oficial": "Plan Progreso para Bolivia - Convergencia Nacional",
        "tipo_organizacion": "ALIANZA_ELECTORAL",
        "es_alianza": True,
        "color_hex": "#C0392B",
        "espectro_politico": "Derecha",
        "fundacion_anio": 2009,
        "disolucion_anio": 2014,
        "alias_conocidos": ["PPB-CN", "CN"],
        "miembros_alianza": [
            {"id_partido_miembro": "NFR", "porcentaje_participacion": 60.0},
            {"id_partido_miembro": "MNR", "porcentaje_participacion": 40.0},
        ],
        "historico_scd": [
            {
                "sigla_historica": "PPB-CN",
                "nombre_historico": "Plan Progreso para Bolivia - Convergencia Nacional",
                "valid_from_year": 2009,
                "valid_to_year": 2014,
                "is_current": False,
            }
        ],
    },
    {
        "id_partido": "UD",
        "sigla_estandar": "UD",
        "nombre_oficial": "Unidad Demócrata",
        "tipo_organizacion": "ALIANZA_ELECTORAL",
        "es_alianza": True,
        "color_hex": "#F39C12",
        "espectro_politico": "Centro-Derecha",
        "fundacion_anio": 2014,
        "disolucion_anio": 2019,
        "alias_conocidos": ["UD", "UD-A"],
        "miembros_alianza": [
            {"id_partido_miembro": "UN", "porcentaje_participacion": 55.0},
            {"id_partido_miembro": "DEMOCRATAS", "porcentaje_participacion": 45.0},
        ],
        "historico_scd": [
            {
                "sigla_historica": "UD",
                "nombre_historico": "Alianza Unidad Demócrata",
                "valid_from_year": 2014,
                "valid_to_year": 2019,
                "is_current": False,
            }
        ],
    },
    {
        "id_partido": "MNR",
        "sigla_estandar": "MNR",
        "nombre_oficial": "Movimiento Nacionalista Revolucionario",
        "tipo_organizacion": "PARTIDO_POLITICO",
        "es_alianza": False,
        "color_hex": "#EC008C",
        "espectro_politico": "Nacionalismo Revolucionario / Centro-Derecha",
        "fundacion_anio": 1942,
        "disolucion_anio": None,
        "alias_conocidos": ["MNR", "MNR-PUEBLO", "MNR-MAR", "MNR-UD"],
        "historico_scd": [
            {
                "sigla_historica": "MNR-H",
                "nombre_historico": "Movimiento Nacionalista Revolucionario Histórico",
                "valid_from_year": 1979,
                "valid_to_year": 1988,
                "is_current": False,
            },
            {
                "sigla_historica": "MNR",
                "nombre_historico": "Movimiento Nacionalista Revolucionario",
                "valid_from_year": 1989,
                "valid_to_year": 2025,
                "is_current": True,
            },
        ],
    },
    {
        "id_partido": "UN",
        "sigla_estandar": "UN",
        "nombre_oficial": "Frente de Unidad Nacional",
        "tipo_organizacion": "PARTIDO_POLITICO",
        "es_alianza": False,
        "color_hex": "#F1C40F",
        "espectro_politico": "Centro",
        "fundacion_anio": 2003,
        "disolucion_anio": None,
        "alias_conocidos": ["UN", "UN-CP", "UN-PAÍS"],
        "historico_scd": [
            {
                "sigla_historica": "UN",
                "nombre_historico": "Frente de Unidad Nacional",
                "valid_from_year": 2003,
                "valid_to_year": 2025,
                "is_current": True,
            }
        ],
    },
    {
        "id_partido": "ADN",
        "sigla_estandar": "ADN",
        "nombre_oficial": "Acción Democrática Nacionalista",
        "tipo_organizacion": "PARTIDO_POLITICO",
        "es_alianza": False,
        "color_hex": "#2C3E50",
        "espectro_politico": "Derecha Conservadora",
        "fundacion_anio": 1979,
        "disolucion_anio": None,
        "alias_conocidos": ["ADN", "A.D.N."],
        "historico_scd": [
            {
                "sigla_historica": "ADN",
                "nombre_historico": "Acción Democrática Nacionalista",
                "valid_from_year": 1979,
                "valid_to_year": 2025,
                "is_current": True,
            }
        ],
    },
    {
        "id_partido": "PDC",
        "sigla_estandar": "PDC",
        "nombre_oficial": "Partido Demócrata Cristiano",
        "tipo_organizacion": "PARTIDO_POLITICO",
        "es_alianza": False,
        "color_hex": "#16A085",
        "espectro_politico": "Democracia Cristiana",
        "fundacion_anio": 1954,
        "disolucion_anio": None,
        "alias_conocidos": ["PDC"],
        "historico_scd": [
            {
                "sigla_historica": "PDC",
                "nombre_historico": "Partido Demócrata Cristiano",
                "valid_from_year": 1954,
                "valid_to_year": 2025,
                "is_current": True,
            }
        ],
    },
    {
        "id_partido": "UCS",
        "sigla_estandar": "UCS",
        "nombre_oficial": "Unidad Cívica Solidaridad",
        "tipo_organizacion": "PARTIDO_POLITICO",
        "es_alianza": False,
        "color_hex": "#00AEEF",
        "espectro_politico": "Centro-Derecha",
        "fundacion_anio": 1989,
        "disolucion_anio": None,
        "alias_conocidos": ["UCS"],
        "historico_scd": [
            {
                "sigla_historica": "UCS",
                "nombre_historico": "Unidad Cívica Solidaridad",
                "valid_from_year": 1989,
                "valid_to_year": 2025,
                "is_current": True,
            }
        ],
    },
    {
        "id_partido": "FRI",
        "sigla_estandar": "FRI",
        "nombre_oficial": "Frente Revolucionario de Izquierda",
        "tipo_organizacion": "PARTIDO_POLITICO",
        "es_alianza": False,
        "color_hex": "#27AE60",
        "espectro_politico": "Centro",
        "fundacion_anio": 1978,
        "disolucion_anio": None,
        "alias_conocidos": ["FRI"],
        "historico_scd": [
            {
                "sigla_historica": "FRI",
                "nombre_historico": "Frente Revolucionario de Izquierda",
                "valid_from_year": 1978,
                "valid_to_year": 2025,
                "is_current": True,
            }
        ],
    },
    {
        "id_partido": "MSM",
        "sigla_estandar": "MSM",
        "nombre_oficial": "Movimiento Sin Miedo",
        "tipo_organizacion": "PARTIDO_POLITICO",
        "es_alianza": False,
        "color_hex": "#2E8B57",
        "espectro_politico": "Centro-Izquierda",
        "fundacion_anio": 1999,
        "disolucion_anio": 2014,
        "alias_conocidos": ["MSM"],
        "historico_scd": [
            {
                "sigla_historica": "MSM",
                "nombre_historico": "Movimiento Sin Miedo",
                "valid_from_year": 1999,
                "valid_to_year": 2014,
                "is_current": False,
            }
        ],
    },
    {
        "id_partido": "DEMOCRATAS",
        "sigla_estandar": "DEMOCRATAS",
        "nombre_oficial": "Movimiento Demócrata Social",
        "tipo_organizacion": "PARTIDO_POLITICO",
        "es_alianza": False,
        "color_hex": "#229954",
        "espectro_politico": "Centro-Derecha Autonomista",
        "fundacion_anio": 2013,
        "disolucion_anio": None,
        "alias_conocidos": ["DEMOCRATAS", "MDS", "VERDES"],
        "historico_scd": [
            {
                "sigla_historica": "VERDES",
                "nombre_historico": "Agrupación Ciudadana Verdes",
                "valid_from_year": 2010,
                "valid_to_year": 2012,
                "is_current": False,
            },
            {
                "sigla_historica": "DEMOCRATAS",
                "nombre_historico": "Movimiento Demócrata Social",
                "valid_from_year": 2013,
                "valid_to_year": 2025,
                "is_current": True,
            },
        ],
    },
    {
        "id_partido": "SOL.BO",
        "sigla_estandar": "SOL.BO",
        "nombre_oficial": "Soberanía y Libertad para Bolivia",
        "tipo_organizacion": "AGRUPACION_CIUDADANA",
        "es_alianza": False,
        "color_hex": "#FFD700",
        "espectro_politico": "Centro",
        "fundacion_anio": 2014,
        "disolucion_anio": None,
        "alias_conocidos": ["SOL.BO", "SOL"],
        "historico_scd": [
            {
                "sigla_historica": "SOL.BO",
                "nombre_historico": "Soberanía y Libertad",
                "valid_from_year": 2014,
                "valid_to_year": 2025,
                "is_current": True,
            }
        ],
    },
    {
        "id_partido": "FPV",
        "sigla_estandar": "FPV",
        "nombre_oficial": "Frente Para la Victoria",
        "tipo_organizacion": "PARTIDO_POLITICO",
        "es_alianza": False,
        "color_hex": "#1B4F72",
        "espectro_politico": "Conservadurismo",
        "fundacion_anio": 2009,
        "disolucion_anio": None,
        "alias_conocidos": ["FPV"],
        "historico_scd": [],
    },
    {
        "id_partido": "PAN-BOL",
        "sigla_estandar": "PAN-BOL",
        "nombre_oficial": "Partido de Acción Nacional Boliviano",
        "tipo_organizacion": "PARTIDO_POLITICO",
        "es_alianza": False,
        "color_hex": "#E74C3C",
        "espectro_politico": "Popular",
        "fundacion_anio": 2018,
        "disolucion_anio": None,
        "alias_conocidos": ["PAN-BOL", "PAN"],
        "historico_scd": [],
    },
    {
        "id_partido": "MTS",
        "sigla_estandar": "MTS",
        "nombre_oficial": "Movimiento Tercer Sistema",
        "tipo_organizacion": "PARTIDO_POLITICO",
        "es_alianza": False,
        "color_hex": "#117A65",
        "espectro_politico": "Indigenismo / Comunitarismo",
        "fundacion_anio": 2018,
        "disolucion_anio": None,
        "alias_conocidos": ["MTS"],
        "historico_scd": [],
    },
    {
        "id_partido": "NFR",
        "sigla_estandar": "NFR",
        "nombre_oficial": "Nueva Fuerza Republicana",
        "tipo_organizacion": "PARTIDO_POLITICO",
        "es_alianza": False,
        "color_hex": "#6C3483",
        "espectro_politico": "Centro-Derecha",
        "fundacion_anio": 1995,
        "disolucion_anio": None,
        "alias_conocidos": ["NFR"],
        "historico_scd": [],
    },
    {
        "id_partido": "MIP",
        "sigla_estandar": "MIP",
        "nombre_oficial": "Movimiento Indígena Pachakuti",
        "tipo_organizacion": "PARTIDO_POLITICO",
        "es_alianza": False,
        "color_hex": "#8E44AD",
        "espectro_politico": "Indianismo Katarista",
        "fundacion_anio": 2000,
        "disolucion_anio": 2006,
        "alias_conocidos": ["MIP"],
        "historico_scd": [],
    },
    {
        "id_partido": "AS",
        "sigla_estandar": "AS",
        "nombre_oficial": "Alianza Social",
        "tipo_organizacion": "AGRUPACION_CIUDADANA",
        "es_alianza": False,
        "color_hex": "#2874A6",
        "espectro_politico": "Regional",
        "fundacion_anio": 2005,
        "disolucion_anio": None,
        "alias_conocidos": ["AS"],
        "historico_scd": [],
    },
    {
        "id_partido": "TODOS",
        "sigla_estandar": "TODOS",
        "nombre_oficial": "Agrupación Ciudadana Todos",
        "tipo_organizacion": "AGRUPACION_CIUDADANA",
        "es_alianza": False,
        "color_hex": "#E67E22",
        "espectro_politico": "Regionalismo Autonomista",
        "fundacion_anio": 2010,
        "disolucion_anio": None,
        "alias_conocidos": ["TODOS"],
        "historico_scd": [],
    },
    {
        "id_partido": "SI",
        "sigla_estandar": "SI",
        "nombre_oficial": "Opción SÍ (Referendo)",
        "tipo_organizacion": "OPCION_REFERENDO",
        "es_alianza": False,
        "color_hex": "#27AE60",
        "espectro_politico": "Referendo",
        "fundacion_anio": 2009,
        "disolucion_anio": None,
        "alias_conocidos": ["SÍ", "SI"],
        "historico_scd": [],
    },
    {
        "id_partido": "NO",
        "sigla_estandar": "NO",
        "nombre_oficial": "Opción NO (Referendo)",
        "tipo_organizacion": "OPCION_REFERENDO",
        "es_alianza": False,
        "color_hex": "#C0392B",
        "espectro_politico": "Referendo",
        "fundacion_anio": 2009,
        "disolucion_anio": None,
        "alias_conocidos": ["NO"],
        "historico_scd": [],
    },
    {
        "id_partido": "5000H",
        "sigla_estandar": "5000H",
        "nombre_oficial": "Opción Límite 5.000 Hectáreas (Referendo Dirimidor 2009)",
        "tipo_organizacion": "OPCION_REFERENDO",
        "es_alianza": False,
        "color_hex": "#2980B9",
        "espectro_politico": "Referendo",
        "fundacion_anio": 2009,
        "disolucion_anio": 2009,
        "alias_conocidos": ["5000H"],
        "historico_scd": [],
    },
    {
        "id_partido": "10000H",
        "sigla_estandar": "10000H",
        "nombre_oficial": "Opción Límite 10.000 Hectáreas (Referendo Dirimidor 2009)",
        "tipo_organizacion": "OPCION_REFERENDO",
        "es_alianza": False,
        "color_hex": "#8E44AD",
        "espectro_politico": "Referendo",
        "fundacion_anio": 2009,
        "disolucion_anio": 2009,
        "alias_conocidos": ["10000H"],
        "historico_scd": [],
    },
]

# Nombres oficiales conocidos para otros partidos nacionales y regionales frecuentes en los CSV
NOMBRES_CONOCIDOS_EXTRA: Dict[str, Tuple[str, str]] = {
    "FREPAB": ("Frente Patriótico Agropecuario de Bolivia", "PARTIDO_POLITICO"),
    "USTB": ("Unión Social de los Trabajadores de Bolivia", "PARTIDO_POLITICO"),
    "BSD": ("Bolivia Social Demócrata", "PARTIDO_POLITICO"),
    "GENTE": ("Agrupación Ciudadana Gente", "AGRUPACION_CIUDADANA"),
    "MUSPA": ("Movimiento de Unidad Social Patriótica", "PARTIDO_POLITICO"),
    "PULSO": ("Pueblos por la Libertad y Soberanía", "AGRUPACION_CIUDADANA"),
    "PVB-IEP": ("Partido Verde de Bolivia - Instrumento de la Ecología Política", "PARTIDO_POLITICO"),
    "JUNTOS": ("Alianza Juntos", "ALIANZA_ELECTORAL"),
    "LIBRE-21": ("Libertad y Democracia Libre 21", "ALIANZA_ELECTORAL"),
    "SUMATE": ("Agrupación Ciudadana Súmate", "AGRUPACION_CIUDADANA"),
    "J.A. LLALLA.L.P.": ("Jallalla La Paz", "AGRUPACION_CIUDADANA"),
    "MOP": ("Movimiento Originario Popular", "AGRUPACION_CIUDADANA"),
    "MPS": ("Movimiento Poder Social", "AGRUPACION_CIUDADANA"),
    "CST": ("Concertación Social y Trabajo", "AGRUPACION_CIUDADANA"),
    "NACER": ("Nacionalidades Autónomas por el Cambio y Empoderamiento Revolucionario", "AGRUPACION_CIUDADANA"),
    "PRIMERO EL BENI": ("Primero el Beni", "AGRUPACION_CIUDADANA"),
    "UNIDOS": ("Alianza Unidos", "ALIANZA_ELECTORAL"),
    "UNIDOS POR TARIJA": ("Alianza Unidos por Tarija", "ALIANZA_ELECTORAL"),
    "UNIDOS.CBBA": ("Alianza Unidos por Cochabamba", "ALIANZA_ELECTORAL"),
    "COMUNIDAD DE TODOS": ("Comunidad de Todos", "ALIANZA_ELECTORAL"),
    "AHORA!": ("Agrupación Ciudadana Ahora!", "AGRUPACION_CIUDADANA"),
    "ASIP": ("Alianza Social Patriótica", "AGRUPACION_CIUDADANA"),
    "ASP": ("Acuerdo Social Patriótico", "AGRUPACION_CIUDADANA"),
    "LIDER": ("Línea de Desarrollo Estratégico Regional", "AGRUPACION_CIUDADANA"),
    "MAR": ("Movimiento Autónomo Regional", "AGRUPACION_CIUDADANA"),
    "UNIR": ("Agrupación Ciudadana UNIR", "AGRUPACION_CIUDADANA"),
}

def construir_tablas_partidos() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Construye dim_partido, dim_partido_scd y bridge_alianza_partido."""
    SEED_PARTIDOS_JSON.write_text(
        json.dumps({"version": "1.0.0", "partidos": CATALOGO_BASE_PARTIDOS}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    dim_rows: List[Dict[str, Any]] = []
    scd_rows: List[Dict[str, Any]] = []
    bridge_rows: List[Dict[str, Any]] = []
    alias_a_id: Dict[str, str] = {}

    for p in CATALOGO_BASE_PARTIDOS:
        id_p = p["id_partido"]
        dim_rows.append(
            {
                "id_partido": id_p,
                "partido_key": id_p,
                "sigla_estandar": p["sigla_estandar"],
                "sigla_partido": p["sigla_estandar"],
                "nombre_oficial": p["nombre_oficial"],
                "nombre_partido": p["nombre_oficial"],
                "tipo_organizacion": p["tipo_organizacion"],
                "es_alianza": bool(p["es_alianza"]),
                "color_hex": p["color_hex"],
                "espectro_politico": p["espectro_politico"],
                "fundacion_anio": p["fundacion_anio"] or 1979,
                "disolucion_anio": p["disolucion_anio"],
                "es_identidad_resuelta": True,
                "motivo_no_resolucion": "",
            }
        )
        for alias in p.get("alias_conocidos", [id_p]):
            alias_a_id[normalizar_para_matching(alias)] = id_p
        
        historicos = p.get("historicos_scd") or [
            {
                "sigla_historica": p["sigla_estandar"],
                "nombre_historico": p["nombre_oficial"],
                "valid_from_year": p["fundacion_anio"] or 1979,
                "valid_to_year": p["disolucion_anio"] or 2025,
                "is_current": p["disolucion_anio"] is None,
            }            
        ]

        for h in historicos:
            scd_rows.append(
                {
                    "id_partido": id_p,
                    "partido_key": id_p,
                    "sigla_estandar": p["sigla_estandar"],
                    "sigla_historica": h["sigla_historica"],
                    "nombre_oficial": h["nombre_historico"],
                    "nombre_historico": h["nombre_historico"],
                    "valid_from_year": int(h["valid_from_year"]),
                    "valid_to_year": int(h["valid_to_year"]),
                    "is_current": bool(h["is_current"]),
                }
            )
        
        for m in p.get("miembros_alianza", []):
            bridge_rows.append(
                {
                    "id_alianza": id_p,
                    "alianza_key": id_p,
                    "id_partido_miembro": m["id_partido_miembro"],
                    "partido_key": m["id_partido_miembro"],
                    "porcentaje_participacion": float(m["porcentaje_participacion"]),
                }
            )
    
    ids_registrador = {r["id_partido"] for r in dim_rows}
    archivos_staging = sorted(STAGING_DIR.glob("eleccion_id=*/data.parquet"))

    for pq in archivos_staging:
        df_st = pd.read_parquet(
            pq, columns=["tipo_proceso", "sigla_partido_raw"]
        ).drop_duplicates()

        for _, row in df_st.iterrows():
            sigla_raw = limpaor_texto(str(row["sigla_partido_raw"]))
            tipo_proc = str(row["tipo_proceso"])
            norm_key = normalizar_para_matching(sigla_raw)

            if norm_key in alias_a_id or sigla_raw in ids_registrados:
                continue
            
            if tipo_proc == "ELECCION_JUDICIAL":
                id_nuevo = f"JUD-{re.sub(r'[^A->0-9]', '', norm_key)[:18]}"
                nombre_of = f"Candidatura Judicial: {sigla_raw.title()}"
                tipo_org = "CANDIDATURA_JUDICIAL"
                resuelta = True
                motivo = ""
            elif norm_key in NOMBRES_CONOCIDOS_EXTRA:
                id_nuevo = sigla_raw
                nombre_of, tipo_org = NOMBRES_CONOCIDOS_EXTRA[norm_key]
                resuelta=True
                motivo = ""
            elif tipo_proc in ("ELECCION_GENERAL", "ELECCION_DEPARTAMENTAL"):
                id_nuevo = sigla_raw
                nombre_of = f"Organizacion Politica {sigla_raw}"
                tipo_org = True
                motivo = ""
            else:
                id_nuevo = f"MUN-{re.sub(r'[^A-Z0-9]', '', norm_key)[:18]}"
                nombre_of = f"Agrupacion Ciudadana Municipal ({sigla_raw})"
                tipo_org = "AGRUPACION_MUNICIPAL_LOCAL"
                resuelta = False
                motivo = (
                    "Sigla de agrupacion ciudadana de alcance estrictamente municipal "
                    "sin genealogía nacional en catálogo maestro del OEP"
                )
            
            if id_nuevo in ids_registrados:
                alias_a_id[norm_key] = id_nuevo
                continue
            
            ids_registrados.add(id_nuevo)
            alias_a_id[norm_key] = id_nuevo

            dim_rows.append(
                {
                    "id_partido": id_nuevo,
                    "partido_key": id_nuevo,
                    "sigla_estandar": sigla_raw,
                    "sigla_partido": sigla_raw,
                    "nombre_oficial": nombre_of,
                    "nombre_partido": nombre_of,
                    "tipo_organizacion": tipo_org,
                    "es_alianza": tipo_org == "ALIANZA_ELECTORAL",
                    "color_hex": "#7F8C8D",
                    "espectro_politico": "Judicial" if tipo_proc == "ELECCION_JUDICIAL" else "Local / Regional",
                    "fundacion_anio": 2005,
                    "disolucion_anio":None,
                    "es_identidad_resuelta": resuelta,
                    "motivo_no_resolucion": motivo,
                }
            )
            scd_rows.append(
                {
                    "id_partido": id_nuevo,
                    "partido_key": id_nuevo,
                    "sigla_estandar": sigla_raw,
                    "sigla_historica": sigla_raw,
                    "nombre_oficial": nombre_of,
                    "nombre_historico": nombre_of,
                    "valid_from_year": 1979,
                    "valid_to_year": 2025,
                    "is_current": True,
                }
            )
    
    df_dim = pd.DataFrame(dim_rows)
    df_scd = pd.DataFrame(scd_rows)
    df_scd.insert(0, "id_scd", range(1, len(df_scd) + 1 ))
    df_bridge = pd.DataFrame(bridge_rows)

    df_dim.to_parquet(DIM_PARTIDO_PARQUET, index=False, compression="snappy")
    df_scd.to_parquet(DIM_PARTIDO_SCD_PARQUET, index=False, compression="snappy")
    df_bridge.to_parquet(BRIDGE_ALIANZA_PARQUET, index=False, compression="snappy")

    logger.info(
        f"[bold green] Tabla partidos construidos [/bold green]"
        f"dim_partido={len(df_dim)}, dim_partido_scd={len(df_scd)}, bridge={len(df_bridge)}."        
    )

    return df_dim, df_scd, df_bridge

def main() -> None:
    df_dim. df_scd, df_bridge = construir_tablas_partidos()
    resumen = (
        df_dim.groupby(["tipo_organizacion", "es_identidad_resuelta"], as_index=False)
        .agg(total=("id_partido", "count"))
        .sort_values("total", ascending=False)
    )

    table = Table(title="Ajllay - Resumen de dim_partido por Tipo de Organizacion", header_style="bold cyan")
    table.add_column("Tipo Organizacion", style="bold yellow")
    table.add_column("Identidad Resuelta", justify="center")
    table.add_column("Cantidad", justify="right", style="green")

    for _, r in resumen.iterrows():
        table.add_row(
            str(r["tipo_organizacion"]),
            "SI" if r["es_identidad_resuelta"] else "NO (Documentada)",
            str(r["total"]),
        )
    console.print(table)

if __name__ == "__main__":
    main()
