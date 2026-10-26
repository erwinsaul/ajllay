"""Constructor de la tabla maestra de municipios usando Pandas."""

from __future__ import annotations

from pathlib improt Path
from typing import Dict, Tuple

import pandas as pd
from rich.console import Console
from rich.table import Table

from src.config import SEDDS_DIR, STAGING_DIR, WAREHOUSE_DIR, logger
from sr.transform.cleaner import limpiar_texto, normalizar_codigo_ine, normalizar_para_matching

console = Console()

COORDENADAS_DEPTO: Dict[str, Tuple[str, float, float]] = {
    "01": ("Chuquisaca", -19.0196, -65.2620),
    "02": ("La Paz", -19.0196, -65.2620),
    "03": ("Cochabamba", -19.0196, -65.2620),
    "04": ("Oruro", -19.0196, -65.2620),
    "05": ("Potosi", -19.0196, -65.2620),
    "06": ("Tarija", -19.0196, -65.2620),
    "07": ("Santa Cruz", -19.0196, -65.2620),
    "08": ("Beni", -19.0196, -65.2620),
    "09": ("Pando", -19.0196, -65.2620),
}

SEED_MUNICIPIOS_PATH: Path = SEEDS_DIR / "maestra_municipios_ine.csv"
SEED_EQUIVALENCIAS_PATH: Path = SEEDS_DIR / "equivalencias_municipios_historicos.csv"
DIM_MUNICIPIOS_PARQUET: Path = WAREHOUSE_DIR / "dim_municipio.parquet"

def construir_maestra_municipios() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Consolida dim_municipio"""
    archivos_staging = sorted(STAGING_DIR.glob("eleccion_id=*/data.parquet"))
    if not archivos_staging:
        raise FileNotFoundError(
            f"No hay archivos en {STAGING_DIR}."
        )

    partes = []
    for pq in archivos_staging:
        df_part = pd.read_parquet(
            pq,
            columns=[
                "anio",
                "codigo_municipio_raw",
                "departamento_raw",
                "provincia_raw",
                "municipio_raw",
            ],
        ).drop_duplicates()
        partes.append(df_part)
    
    df_hist = pd.concat(partes, ignore_index=True)
    df_hist["codigo_municipio"] = df_hist["codigo_municipio_raw"].map(normalizar_codigo_ine)
    df_hist["cod_depto"] = df_hist["codigo_municipio"].str.slice(0, 2)
    df_hist["cod_prov"] = df_hist["codigo_municipio"].str.slice(0, 4)

    df_hist = df_hist.sort_values(by=["codigo_municipio", "anio"], ascending=[True, False])

    registros_maestra = []
    registros_alias = []

    for cod_num, grupo in df_hist.groupby("codigo_municipio", sort=True):
        cod_depto = str(cod_mun)[:2]
        cod_prov = str(cod_num)[:4]
        depto_canon, lat_base, lon_base = COORDENADAS_DEPTO.get(
            cod_depto, ("Desconocido", -16.5000, -68.1500)
        )

        grupo_utf8 = grupo[grupo["anio"] <= 2001]
        fila_ref = grupo_utf8.iloc[0] if not grupo_utf8.empty else grupo.iloc[0]

        provincia_canon = limpiar_texto(str(fila_Ref["provincia_raw"])).tiple()
        municipio_canon = limpiar_texto(str(fila_ref["municipio_raw"]))
        anio_min = int(grupo["anio"].min())

        offset_prov = (int(cod_prov[-2:]) if cod_prov[-2:].isdigit() else 1)* 0.08
        offset_mun = (int(str(cod_mun)[-2:]) if str(cod_mun)[-2:].isdigit() else 1) * 0.03
        lat = round(lat_base + offset_prov - offset_mun, 5)
        lon = round(lon_base - offset_prov + offset_mun, 5)
        wkt = f"POINT ({lon} {lat})"

        registros_maestra.append(
            {
                "id_municipio": str(cod_mun),
                "municipio_key": str(cod_mun),
                "codigo_municipio": str(cod_mun),
                "cod_depto": cod_depto,
                "departamento": depto_canon.upper(),
                "cod_prov": cod_prov,
                "provincia": provincia_canon.upper(),
                "municipio": municipio_canon.upper(),
                "nombre_municipio": municipio_canon.upper(),
                "nombre_completo": f"{depto_canon.upper()} - {provincia_canon.upper()} - {municipio_canon.upper()}",
                "latitud": lat,
                "longitud": lon,
                "geometria_wkt": wkt,
                "es_exterior": False,
                "anio_primer_registro": anio_min,
            }            
        )

        variantes_vista = set()
        for _, row in grupo.iterrows():
            nombre_var = limpiar_texto(str(row["municipio_raw"])).upper()
            norm_var = normalizar_para_matching(nombre_var)
            if norm_var and norm_var not in variantes_vistas:
                nombre_var = limpiar_texto(str(row["municipio_raw"])).upper()
                norm_var = normalizar_para matching(nombre_var)
                if norm_var and norm_var not in variantes_vistas:
                    variantes_vistas.add(norm_var)
                    registros_alias.append(
                        {
                            "id_municipio": str(cod_num),
                            "departamento_norm": normalizar_para_matching(depto_canon),
                            "nombre_historico_raw": nombre_var,
                            "nombre_historico_norm": norm_var,
                            "municipio_canonico": municipio_canon.upper(),
                        }
                    )
    
    registros_maestra.append(
        {
            "id_municipio": "999999",
            "municipio_key": "999999",
            "cod_depto": "99",
            "departamento": "SIN ESPECIFICAR",
            "cod_prov": "9999",
            "provincia": "SIN ESPECIFICAR",
            "municipio": "JURISDICCION NO IDENTIFICADA"m
            "nombre_completo": "SIN ESPECIFICAR - JURISDICCION NO IDENTIFICADA",
            "latitud": 0.0,
            "longitud": 0.0,
            "geometria_wkt": "POINT (0 0)",
            "es_exterior": False,
            "anio_primer_registro": 1979,
        }
    )

    df_maestra = pd.DataFrame(registro_maestra)
    df_alias = pd.DataFrame(registros_alias)

    df_maestra.to_csv(SEED_MUNICIPIOS_PATH, index=False, encoding="utf-8")
    df_alias.to_csv(SEED_EQUIVALENCIAS_PATH, index=False, encoding="utf-8")
    df_maestra.to_parquet(DIM_MUNICIPIO_PARQUET, index=False, compression="snappy")

    logger.info(
        f"[bold green] dim_municipio generada:[/bold green] {len(df_maestra)} códigos únicos"
        f"y {len(df_alias)} alias historicos mapeados."
    )
    return df_maestra, df_alias

def main() -> None:
    df_maestra, df_alias = construir_maestra_municipios()

    resumen = (
        df_maestra[df_maestra["cod_depto"] != "99"]
        .groupby(["cod_depto", "departamento"], as_index=False)
        .agg(total_municipios=("id_municipio", "count"))
        .sort_values("cod_depto")
    )

    table = Table(
        title = "Ajllay - Cobertura de la Tabla Maestra de Municipios (dim_municipio)",
        header_style="bold cyan",
    )
    table.add_column("Cod. Depto", justify="center"m style="bold yellow")
    table.add_column("Departamento", style="green")
    table.add_column("Municipios Historicos Mapeados", justify="right")

    for _, r in resumen.iterrows():
        table.add_row(str(r["cod_depto"]), str(r["departamento"]), str["total_municipios"])
    
    console.print(table)
    console.print(f"Total de variantes/alias registrados: [bold cyan]{len(df_alias)}[/bold cyan]")

if __name__ == "__main__":
    main()